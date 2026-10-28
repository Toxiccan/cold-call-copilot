# Cold Call Copilot

A call-side guide for salespeople speaking with company leaders. The product is intended to show one conversation stage at a time, capture the prospect's exact words, preserve call progress, and offer optional AI suggestions without taking control from the salesperson.

## Current project status

| Project stage | Status | Notes |
|---|---|---|
| Inspect the assignment, reference screen, workspace, and transcript bundle | Complete | The reference calls for a one-stage-at-a-time guide and a past-calls view. |
| Define the architecture and database schema | Complete | React + Vite, FastAPI, Supabase PostgreSQL, and Gemini planned. The initial `calls` and `call_stages` migration has been applied to Supabase. |
| Build the first persistence workflow | Backend implemented; partly verified | Create and list calls were exercised through FastAPI docs. Retrieve, stage save/update, resume, and close still need a full manual workflow check. |
| Build the reference-inspired call screens | Implemented; local verification pending | The active-call and history views are wired to the backend API. Phase 4 uses the assignment’s existing eight-stage flow and transcript-backed examples; no extra stages are added. |
| Add Gemini assistance and fallback behavior | Implemented; live Gemini verification pending | Suggestions include uncertainty, use earlier saved stages, and never advance or close a call. A local fallback is used when Gemini is unavailable. |
| Analyze transcripts and refine prompts/outcomes | In progress | All call endings and source metadata were reviewed; Gemini uses transcript-informed intent labels and paraphrased stage patterns, with a 12-case synthetic evaluation set. Live model evaluation and validated stage annotations remain. Preserve source labels; `not_logged` must not become `not_interested`. |
| Test the complete application | Not started | Verify persistence, navigation, resume, close, errors, and AI fallback behavior. |
| Deploy to Supabase, Render, and Vercel | Not started | Production URLs and deployment success are not yet available. |
| Finish documentation and walkthrough preparation | In progress | Setup and progress notes are documented; the six-minute walkthrough script remains to be prepared. |

## Architecture

- **Frontend:** React and Vite. It will call FastAPI and must not contain privileged Supabase or Gemini keys.
- **Backend:** FastAPI. It validates call data, reads and writes Supabase records, and calls Gemini for optional suggestions when configured.
- **Database:** Supabase PostgreSQL. The schema migration is in `supabase/migrations/`.
- **AI:** Gemini, called only from the backend when configured, with a useful local fallback.

## Local setup

- Backend setup, environment variables, and endpoints: [`backend/README.md`](backend/README.md)
- Frontend setup and planned caller workflow: [`frontend/README.md`](frontend/README.md)

## Transcript data

Use the supplied fictional transcript bundle locally in `cold-call-transcripts-100/` for analysis and prompt evaluation. The folder is excluded from Git because the bundle is for this assignment's use and should not be published. Some speaker labels may be incorrect; preserve recorded outcomes as original labels and store inferred outcomes separately with uncertainty.

Aggregate outcome counts and current prompt decisions are documented in [`docs/transcript-analysis.md`](docs/transcript-analysis.md); no transcript excerpts are included.

## Assignment references

- [Assignment structure](https://sainikpuri.deepthought.education/fde-hyderabad-v2/structure)
- [Reference screen](https://sainikpuri.deepthought.education/fde-hyderabad-v2/reference)
