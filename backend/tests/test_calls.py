"""Isolated tests for call routes using an in-memory Supabase substitute."""

import unittest
import os
import json
from io import BytesIO
from datetime import datetime, timezone
from unittest.mock import patch
from uuid import UUID, uuid4

from fastapi import HTTPException

from app import main
from app.routes import calls
from app.services import gemini
from app.services.transcript_guidance import EVALUATION_CASES, INTENT_LABELS, prompt_guidance


class Result:
    def __init__(self, data):
        self.data = data


class Query:
    def __init__(self, database, table):
        self.database = database
        self.table = table
        self.operation = "select"
        self.values = None
        self.filters = {}
        self.ordering = None
        self.with_stages = False
        self.single = False

    def select(self, columns):
        self.with_stages = "call_stages(*)" in columns
        return self

    def insert(self, values):
        self.operation, self.values = "insert", values
        return self

    def update(self, values):
        self.operation, self.values = "update", values
        return self

    def upsert(self, values, on_conflict=None):
        self.operation, self.values = "upsert", values
        return self

    def eq(self, key, value):
        self.filters[key] = value
        return self

    def order(self, key, desc=False):
        self.ordering = (key, desc)
        return self

    def limit(self, _count):
        return self

    def maybe_single(self):
        self.single = True
        return self

    def execute(self):
        if self.database.fail_queries:
            raise RuntimeError("simulated database failure")
        rows = self.database.tables[self.table]
        matching = [
            row for row in rows
            if all(row.get(key) == value for key, value in self.filters.items())
        ]

        if self.operation == "insert":
            row = dict(self.values)
            row.update({
                "id": str(uuid4()),
                "started_at": datetime.now(timezone.utc).isoformat(),
                "status": "in_progress",
                "last_stage": 1,
                "outcome": None,
                "ended_at": None,
                "duration_seconds": None,
                "outcome_source": None,
            })
            rows.append(row)
            return Result([row])

        if self.operation == "update":
            for row in matching:
                row.update(self.values)
            return Result(matching)

        if self.operation == "upsert":
            row = next((row for row in rows if
                        row["call_id"] == self.values["call_id"] and
                        row["stage_number"] == self.values["stage_number"]), None)
            if row is None:
                row = dict(self.values)
                rows.append(row)
            else:
                row.update(self.values)
            return Result([row])

        if self.ordering:
            key, descending = self.ordering
            matching.sort(key=lambda row: row.get(key) or "", reverse=descending)
        if self.with_stages:
            for call in matching:
                call["call_stages"] = [
                    stage for stage in self.database.tables["call_stages"]
                    if stage["call_id"] == call["id"]
                ]
        if self.single:
            return Result(matching[0] if matching else None)
        return Result(matching)


class FakeDatabase:
    def __init__(self):
        self.tables = {"calls": [], "call_stages": []}
        self.fail_queries = False

    def table(self, name):
        return Query(self, name)


class CallRouteTests(unittest.TestCase):
    def setUp(self):
        self.database = FakeDatabase()
        self.client_patch = patch.object(calls, "get_supabase_client", lambda: self.database)
        self.health_patch = patch.object(main, "check_supabase_connection", lambda: True)
        self.client_patch.start()
        self.health_patch.start()
        self.addCleanup(self.client_patch.stop)
        self.addCleanup(self.health_patch.stop)

    def create_call(self, name="Alex", company=None):
        return calls.create_call(calls.CallCreate(prospect_name=name, company_name=company))

    def test_create_trims_name_and_keeps_optional_company(self):
        created = self.create_call("  Alex Morgan  ", "Acme")
        self.assertEqual(created["prospect_name"], "Alex Morgan")
        self.assertEqual(created["company_name"], "Acme")
        self.assertEqual(created["status"], "in_progress")

    def test_create_rejects_blank_name(self):
        with self.assertRaises(HTTPException) as raised:
            calls.create_call(calls.CallCreate(prospect_name="   "))
        self.assertEqual(raised.exception.status_code, 422)

    def test_fallback_honors_do_not_call_intent(self):
        result = gemini.fallback_suggestions(6, "Please do not call this number again.")
        self.assertEqual(result["likely_intent"], "do_not_call")
        self.assertIn("Respect the request", result["recommended_next_action"])

    def test_save_update_resume_and_list_stage(self):
        created = self.create_call()
        call_id = UUID(created["id"])
        first = calls.CallStageSave(
            response_category="Ready to hear more", prospect_words="Tell me more", notes="First"
        )
        calls.save_call_stage(call_id, 3, first)
        updated = calls.CallStageSave(
            response_category="Ready to hear more", prospect_words="Tell me more", notes="Updated"
        )
        calls.save_call_stage(call_id, 3, updated)

        self.assertEqual(len(self.database.tables["call_stages"]), 1)
        resumed = calls.get_call(call_id)
        self.assertEqual(resumed["last_stage"], 3)
        self.assertEqual(resumed["call_stages"][0]["notes"], "Updated")
        self.assertEqual(calls.list_calls()["calls"][0]["id"], created["id"])

    def test_close_records_caller_outcome_and_blocks_later_changes(self):
        created = self.create_call()
        call_id = UUID(created["id"])
        closed = calls.close_call(call_id, calls.CallClose(outcome="follow_up"))

        self.assertEqual(closed["status"], "completed")
        self.assertEqual(closed["outcome"], "follow_up")
        self.assertEqual(closed["outcome_source"], "caller_selected")
        self.assertIsNotNone(closed["ended_at"])
        self.assertGreaterEqual(closed["duration_seconds"], 0)
        with self.assertRaises(HTTPException) as raised:
            calls.save_call_stage(call_id, 1, calls.CallStageSave())
        self.assertEqual(raised.exception.status_code, 409)

    def test_missing_calls_return_not_found(self):
        missing_id = uuid4()
        with self.assertRaises(HTTPException) as get_error:
            calls.get_call(missing_id)
        self.assertEqual(get_error.exception.status_code, 404)
        with self.assertRaises(HTTPException) as close_error:
            calls.close_call(missing_id, calls.CallClose(outcome="follow_up"))
        self.assertEqual(close_error.exception.status_code, 404)

    def test_database_failure_is_reported_as_gateway_error(self):
        self.database.fail_queries = True
        with self.assertRaises(HTTPException) as raised:
            calls.list_calls()
        self.assertEqual(raised.exception.status_code, 502)

    def test_analyze_returns_fallback_and_uses_saved_prior_stage_context(self):
        created = self.create_call()
        call_id = UUID(created["id"])
        calls.save_call_stage(
            call_id,
            1,
            calls.CallStageSave(prospect_words="Hello", notes="Reached the director"),
        )
        request = calls.CallAnalyzeRequest(
            stage_number=2,
            prospect_words="What is this about?",
        )
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
            result = calls.analyze_call_suggestions(call_id, request)

        self.assertEqual(result["source"], "fallback")
        self.assertEqual(result["likely_stage_number"], 2)
        self.assertEqual(result["likely_intent"], "asking_purpose")
        self.assertEqual(len(result["suggested_responses"]), 3)

    def test_analyze_passes_earlier_stage_notes_to_the_model(self):
        created = self.create_call()
        call_id = UUID(created["id"])
        calls.save_call_stage(
            call_id,
            1,
            calls.CallStageSave(
                response_category="Ready to hear more",
                prospect_words="I have a few minutes.",
                notes="Keep the explanation brief.",
            ),
        )
        request = calls.CallAnalyzeRequest(stage_number=2, prospect_words="What is this about?")
        expected = [{
            "stage_number": 1,
            "response_category": "Ready to hear more",
            "prospect_words": "I have a few minutes.",
            "notes": "Keep the explanation brief.",
        }]
        with patch.object(calls, "analyze_call_with_gemini", return_value={"source": "gemini"}) as model:
            calls.analyze_call_suggestions(call_id, request)

        model.assert_called_once_with(2, "What is this about?", expected)

    def test_analyze_rejects_missing_call(self):
        request = calls.CallAnalyzeRequest(stage_number=1, prospect_words="Hello")
        with self.assertRaises(HTTPException) as raised:
            calls.analyze_call_suggestions(uuid4(), request)
        self.assertEqual(raised.exception.status_code, 404)

    def test_analyze_request_rejects_out_of_range_stage(self):
        with self.assertRaises(ValueError):
            calls.CallAnalyzeRequest(stage_number=9, prospect_words="Hello")

    def test_gemini_response_is_parsed_and_labeled(self):
        model_json = {
            "likely_stage_number": 2,
            "likely_intent": "asking_purpose",
            "explanation": "The prospect is asking about the call's purpose.",
            "suggested_responses": ["Reply one.", "Reply two.", "Reply three."],
            "recommended_next_action": "Briefly explain the purpose.",
            "uncertainty": "low",
        }
        provider_payload = {
            "candidates": [{
                "content": {"parts": [{"text": json.dumps(model_json)}]}
            }]
        }
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}), patch.object(
            gemini,
            "urlopen",
            return_value=BytesIO(json.dumps(provider_payload).encode()),
        ) as mocked_urlopen:
            result = gemini.analyze_call(2, "What is this about?", [])

        self.assertEqual(result["source"], "gemini")
        self.assertEqual(result["likely_stage_number"], 2)
        self.assertEqual(result["likely_intent"], "asking_purpose")
        self.assertEqual(len(result["suggested_responses"]), 3)
        request_body = json.loads(mocked_urlopen.call_args.args[0].data)
        prompt_context = json.loads(request_body["contents"][0]["parts"][0]["text"])
        self.assertIn("transcript_informed_guidance", prompt_context)
        self.assertEqual(
            len(prompt_context["transcript_informed_guidance"]["stage_patterns"]), 2
        )

    def test_stage_prompt_uses_paraphrased_transcript_patterns(self):
        guidance = prompt_guidance(6)
        combined = " ".join(item["pattern"] for item in guidance["stage_patterns"])
        self.assertIn("not interested", combined)
        self.assertIn("no further calls", combined)
        self.assertIn("not transcript quotes", guidance["note"])

    def test_synthetic_evaluation_cases_use_supported_intents(self):
        self.assertGreaterEqual(len(EVALUATION_CASES), 10)
        self.assertTrue(all(case["intent"] in INTENT_LABELS for case in EVALUATION_CASES))

    def test_fallback_intent_rules_cover_synthetic_evaluation_cases(self):
        mismatches = [
            (case["intent"], gemini.fallback_suggestions(case["stage"], case["words"])["likely_intent"])
            for case in EVALUATION_CASES
            if gemini.fallback_suggestions(case["stage"], case["words"])["likely_intent"] != case["intent"]
        ]
        self.assertEqual(mismatches, [])

    def test_health_handlers(self):
        self.assertEqual(main.health_check(), {"status": "ok"})
        self.assertEqual(main.supabase_health_check(), {"status": "ok", "supabase": "connected"})

    def test_analyze_endpoint_is_registered(self):
        self.assertIn("/calls/{call_id}/analyze", main.app.openapi()["paths"])


if __name__ == "__main__":
    unittest.main()
