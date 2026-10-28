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

## Module 1 status: Complete

- Supabase schema and call-management routes are implemented and deployed.
- The frontend supports the full call workflow: create, stage save/update, resume, history, and close with a caller-selected outcome.
- Optional suggestions use current prospect words and earlier saved stages. Gemini calls stay on the backend; a safe local fallback is returned when Gemini is unavailable.
- All 17 backend unit tests passed. Three live callback, objection, and do-not-call scenarios returned appropriate intent classifications and suggestions. In those live checks, the UI identified the source as fallback and uncertainty as high.
- Frontend lint and production build passed. Deployment addresses and project status are in the [root README](../README.md).

Transcript observations, source outcome handling, and prompt decisions are documented in [`../docs/transcript-analysis.md`](../docs/transcript-analysis.md).
