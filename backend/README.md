# Backend

FastAPI service for call management, Supabase persistence, and optional Gemini coaching.

## Local setup

1. Copy `.env.example` to `.env` in this directory. Set `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` to your project URL and backend-only secret/service-role key. `GEMINI_API_KEY` is optional: leave it blank to use fallback suggestions, or provide a Gemini API key to enable AI suggestions. `GEMINI_MODEL` defaults to `gemini-3.5-flash-lite`. `FRONTEND_ORIGIN` is optional for local development; set it to the deployed frontend origin in production. Keep secret keys in the backend only; never commit `.env` or place keys in frontend code.
2. From this `backend` directory, install dependencies and start the development server:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
   ```

3. Open `http://127.0.0.1:8000/docs` for interactive API documentation.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Check that FastAPI is responding. |
| `GET` | `/health/supabase` | Check backend access to the Supabase `calls` table. |
| `POST` | `/calls` | Create an in-progress call with a prospect name and optional company name. |
| `GET` | `/calls` | List calls newest first for history. |
| `GET` | `/calls/{call_id}` | Retrieve a call and its saved stages for resuming. |
| `PUT` | `/calls/{call_id}/stages/{stage_number}` | Save or update one stage (1–8), with category, exact words, and notes. |
| `POST` | `/calls/{call_id}/analyze` | Analyze current words and earlier saved stages; returns likely stage and intent, suggestions, next action, uncertainty, and source (`gemini` or `fallback`). |
| `POST` | `/calls/{call_id}/close` | Close a call with a caller-selected outcome and record end time and duration. |

Closing a call sets `outcome_source` to `caller_selected`. Transcript source labels belong in `original_outcome`; inferred outcomes remain separate and must not overwrite `not_logged`.

## Database

Apply `../supabase/migrations/202610270001_create_calls_and_call_stages.sql` to Supabase before starting the API. It defines the `calls` and `call_stages` tables and their constraints.

## Progress

- **Completed:** Supabase schema, local environment configuration, health checks, and call create/list/retrieve/stage-save/close routes.
- **Partly verified:** call creation and listing were manually checked through `/docs`.
- **Implemented:** reference-inspired frontend workflow and optional Gemini suggestions with a local fallback. Gemini runs only on the backend; the caller remains in control.
- **Still to verify:** complete manual workflow against Supabase and live Gemini behavior after `GEMINI_API_KEY` is configured.
- **In progress:** source outcomes and all call endings have been reviewed; transcript-informed intent labels, stage patterns, and a 12-case synthetic evaluation set are implemented. Run `.\.venv\Scripts\python.exe scripts\evaluate_gemini.py` from the backend directory for the live prompt check; it sends only synthetic paraphrases to Gemini.
- **Planned:** deployment and full end-to-end verification.
