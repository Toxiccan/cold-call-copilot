# Cold Call Copilot

A call-side guide for salespeople speaking with company leaders. It presents the assignment's existing conversation stages one at a time, records the prospect's words and call progress, and offers optional response suggestions while leaving decisions with the salesperson.

## Module 1 status: Complete

The application is implemented and deployed with a React + Vite frontend, FastAPI backend, and Supabase PostgreSQL database.

- **Call workflow:** Start calls, move through the existing eight stages, save and revise stage details, resume in-progress calls, and review call history.
- **Call outcomes:** End a call at any stage and record the caller-selected outcome and call duration.
- **Suggestions:** Request likely intent, stage, uncertainty, three possible replies, and a next action based on the current prospect words and earlier saved stages. Gemini is called from the backend; local fallback suggestions are available when Gemini is unavailable.
- **Data and secrets:** Calls and stages are stored in Supabase. Privileged Supabase and Gemini keys stay on the backend.
- **Deployment:** The frontend is on [Vercel](https://cold-call-copilot-nine.vercel.app/) and the API is on [Render](https://cold-call-copilot-k6u4.onrender.com/). Supabase hosts the database.
- **Verification:** All 17 backend unit tests passed; frontend lint and production build passed. Three live scenarios (callback request, objection, and do-not-call request) produced appropriate suggestions. The live UI identified those three results as fallback suggestions with high uncertainty.

## Architecture

- **Frontend:** React and Vite. It calls FastAPI and contains no privileged Supabase or Gemini keys.
- **Backend:** FastAPI validates calls and stages, reads and writes Supabase records, and requests optional Gemini suggestions.
- **Database:** Supabase PostgreSQL. The `calls` and `call_stages` schema is defined in `supabase/migrations/`.
- **Suggestions:** Gemini is optional. The backend returns safe, stage-aware fallback suggestions when Gemini is unavailable.

## Local setup

- Backend setup, environment variables, endpoints, and verification: [`backend/README.md`](backend/README.md)
- Frontend setup and workflow: [`frontend/README.md`](frontend/README.md)

## Transcript data

The supplied fictional transcript bundle in `cold-call-transcripts-100/` is for local analysis and is excluded from Git. Aggregate observations and prompt decisions are documented in [`docs/transcript-analysis.md`](docs/transcript-analysis.md); source transcript excerpts are not included.

## Assignment references

- [Assignment structure](https://sainikpur.deepthought.education/fde-hyderabad-v2/structure)
- [Reference screen](https://sainikpur.deepthought.education/fde-hyderabad-v2/reference)
