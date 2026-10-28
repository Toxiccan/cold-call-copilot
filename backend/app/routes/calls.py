from datetime import datetime, timezone
from typing import Any, Literal
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, Field

from app.database import get_supabase_client
from app.services.gemini import analyze_call as analyze_call_with_gemini


router = APIRouter(prefix="/calls", tags=["calls"])


class CallCreate(BaseModel):
    prospect_name: str = Field(min_length=1, max_length=200)
    company_name: str | None = Field(default=None, max_length=200)


class CallStageSave(BaseModel):
    response_category: str | None = Field(default=None, max_length=200)
    prospect_words: str | None = Field(default=None, max_length=10000)
    notes: str | None = Field(default=None, max_length=5000)


class CallAnalyzeRequest(BaseModel):
    stage_number: int = Field(ge=1, le=8)
    prospect_words: str = Field(default="", max_length=10000)


CallOutcome = Literal[
    "next_step_agreed",
    "agreed_to_receive_report",
    "follow_up",
    "interested",
    "not_interested",
    "do_not_call",
    "wrong_person",
    "moved_company",
    "call_again",
    "no_answer",
    "unknown",
    "not_logged",
]


class CallClose(BaseModel):
    outcome: CallOutcome


@router.post("", status_code=201)
def create_call(call: CallCreate) -> dict[str, Any]:
    """Create a call; the database supplies its ID, timestamp, and status."""
    values = call.model_dump(exclude_none=True)
    values["prospect_name"] = values["prospect_name"].strip()

    if not values["prospect_name"]:
        raise HTTPException(status_code=422, detail="Prospect name cannot be blank.")

    try:
        result = get_supabase_client().table("calls").insert(values).execute()
        return result.data[0]
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not create the call. Check the backend and Supabase connection.",
        ) from exc


@router.get("")
def list_calls() -> dict[str, list[dict[str, Any]]]:
    """Return saved calls newest first for the history screen."""
    try:
        result = (
            get_supabase_client()
            .table("calls")
            .select("*")
            .order("started_at", desc=True)
            .execute()
        )
        return {"calls": result.data}
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not load call history. Check the backend and Supabase connection.",
        ) from exc


@router.put("/{call_id}/stages/{stage_number}")
def save_call_stage(
    call_id: UUID,
    stage_number: int = Path(ge=1, le=8),
    stage: CallStageSave = ...,
) -> dict[str, Any]:
    """Save or revise one stage and record the furthest stage reached."""
    call_key = str(call_id)

    try:
        client = get_supabase_client()
        call_result = (
            client.table("calls")
            .select("id, status, last_stage")
            .eq("id", call_key)
            .maybe_single()
            .execute()
        )
        call = call_result.data
        if call is None:
            raise HTTPException(status_code=404, detail="Call not found.")
        if call["status"] == "completed":
            raise HTTPException(status_code=409, detail="This call is already completed.")

        stage_values = stage.model_dump()
        stage_values.update({"call_id": call_key, "stage_number": stage_number})
        saved_stage = (
            client.table("call_stages")
            .upsert(stage_values, on_conflict="call_id,stage_number")
            .execute()
        )

        furthest_stage = max(call.get("last_stage") or 0, stage_number)
        client.table("calls").update({"last_stage": furthest_stage}).eq(
            "id", call_key
        ).execute()
        return saved_stage.data[0]
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not save this stage. Check the backend and Supabase connection.",
        ) from exc


@router.post("/{call_id}/close")
def close_call(call_id: UUID, closing: CallClose) -> dict[str, Any]:
    """Complete a call with the outcome selected by the caller."""
    call_key = str(call_id)

    try:
        client = get_supabase_client()
        call_result = (
            client.table("calls")
            .select("id, status, started_at")
            .eq("id", call_key)
            .maybe_single()
            .execute()
        )
        call = call_result.data
        if call is None:
            raise HTTPException(status_code=404, detail="Call not found.")
        if call["status"] == "completed":
            raise HTTPException(status_code=409, detail="This call is already completed.")

        ended_at = datetime.now(timezone.utc)
        started_at = datetime.fromisoformat(call["started_at"].replace("Z", "+00:00"))
        duration_seconds = max(0, int((ended_at - started_at).total_seconds()))

        result = (
            client.table("calls")
            .update(
                {
                    "status": "completed",
                    "ended_at": ended_at.isoformat(),
                    "duration_seconds": duration_seconds,
                    "outcome": closing.outcome,
                    "outcome_source": "caller_selected",
                }
            )
            .eq("id", call_key)
            .execute()
        )
        return result.data[0]
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not close this call. Check the backend and Supabase connection.",
        ) from exc


@router.get("/{call_id}")
def get_call(call_id: UUID) -> dict[str, Any]:
    """Retrieve one call and its saved stages."""
    try:
        result = (
            get_supabase_client()
            .table("calls")
            .select("*, call_stages(*)")
            .eq("id", str(call_id))
            .maybe_single()
            .execute()
        )

        if result.data is None:
            raise HTTPException(status_code=404, detail="Call not found.")

        return result.data
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not load this call. Check the backend and Supabase connection.",
        ) from exc


@router.post("/{call_id}/analyze")
def analyze_call_suggestions(
    call_id: UUID, request: CallAnalyzeRequest
) -> dict[str, Any]:
    """Suggest possible replies using current words and saved earlier stages."""
    call_key = str(call_id)
    try:
        client = get_supabase_client()
        call_result = (
            client.table("calls")
            .select("id")
            .eq("id", call_key)
            .maybe_single()
            .execute()
        )
        if call_result.data is None:
            raise HTTPException(status_code=404, detail="Call not found.")

        stage_result = (
            client.table("call_stages")
            .select("stage_number, response_category, prospect_words, notes")
            .eq("call_id", call_key)
            .order("stage_number")
            .execute()
        )
        previous_stages = [
            {
                "stage_number": stage["stage_number"],
                "response_category": stage.get("response_category"),
                "prospect_words": (stage.get("prospect_words") or "")[:2000],
                "notes": (stage.get("notes") or "")[:1000],
            }
            for stage in (stage_result.data or [])
            if stage["stage_number"] < request.stage_number
        ]
        return analyze_call_with_gemini(
            request.stage_number,
            request.prospect_words,
            previous_stages,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not analyze this call. Check the backend and Supabase connection.",
        ) from exc
    
    
