# Cold Call Copilot

A call-side guide for salespeople speaking with company leaders. The product is intended to show one conversation stage at a time, capture the prospect's exact words, preserve call progress, and offer optional AI suggestions without taking control from the salesperson.

## Current project status

| Project stage | Status | Notes |
|---|---|---|
| Inspect the assignment, reference screen, workspace, and transcript bundle | Complete | The reference calls for a one-stage-at-a-time guide and a past-calls view. |
| Define the architecture and database schema | Complete | React + Vite, FastAPI, Supabase PostgreSQL, and Gemini planned. The initial `calls` and `call_stages` migration has been applied to Supabase. |
| Build the first persistence workflow | Backend implemented; partly verified | Create and list calls were exercised through FastAPI docs. Retrieve, stage save/update, resume, and close still need a full manual workflow check. |
| Build all eight stages and the call/history interface | In progress | The React + Vite + ESLint scaffold exists. Caller-facing screens and stage guidance have not been implemented yet. |
| Add Gemini assistance and fallback behavior | Not started | Suggestions must remain optional and must not advance or close calls automatically. |
| Analyze transcripts and refine prompts/outcomes | Not started | Preserve source labels and keep inferences separate; `not_logged` must not become `not_interested`. |
| Test the complete application | Not started | Verify persistence, navigation, resume, close, errors, and AI fallback behavior. |
| Deploy to Supabase, Render, and Vercel | Not started | Production URLs and deployment success are not yet available. |
| Finish documentation and walkthrough preparation | In progress | Setup and progress notes are documented; the six-minute walkthrough script remains to be prepared. |

## Architecture

- **Frontend:** React and Vite. It will call FastAPI and must not contain privileged Supabase or Gemini keys.
- **Backend:** FastAPI. It validates call data, reads and writes Supabase records, and will call Gemini for optional suggestions.
- **Database:** Supabase PostgreSQL. The schema migration is in `supabase/migrations/`.
- **AI:** Gemini, called only from the backend, with a useful non-AI fallback.

## Local setup

- Backend setup, environment variables, and endpoints: [`backend/README.md`](backend/README.md)
- Frontend setup and planned caller workflow: [`frontend/README.md`](frontend/README.md)

## Transcript data

The fictional transcript bundle is in `cold-call-transcripts-100/`. Its README explains the format and cautions that some speaker labels may be incorrect. Preserve recorded outcomes as original labels and store inferred outcomes separately with uncertainty.

## Assignment references

- [Assignment structure](https://sainikpuri.deepthought.education/fde-hyderabad-v2/structure)
- [Reference screen](https://sainikpuri.deepthought.education/fde-hyderabad-v2/reference)
