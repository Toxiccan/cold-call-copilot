# Backend

FastAPI service for call management and Supabase persistence. Gemini assistance is planned but not implemented yet.

## Local setup

1. Create `backend/.env` using `.env.example` as a guide. Set `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` to your project values. Keep the secret key in the backend only; never commit `.env` or place it in frontend code.
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
| `POST` | `/calls/{call_id}/close` | Close a call with a caller-selected outcome and record end time and duration. |

Closing a call sets `outcome_source` to `caller_selected`. Transcript source labels belong in `original_outcome`; inferred outcomes remain separate and must not overwrite `not_logged`.

## Database

Apply `../supabase/migrations/202610270001_create_calls_and_call_stages.sql` to Supabase before starting the API. It defines the `calls` and `call_stages` tables and their constraints.

## Progress

- **Completed:** Supabase schema, local environment configuration, health checks, and call create/list/retrieve/stage-save/close routes.
- **Partly verified:** call creation and listing were manually checked through `/docs`.
- **Still to verify:** saving/updating a stage, retrieving saved stage data, closing a call, and seeing the completed call in history.
- **Planned:** frontend integration, Gemini suggestions and fallback, deployment, and end-to-end verification.
