# Project notes and completion stages

The project overview and current milestone status are maintained in the [root README](../README.md). This file records the implementation sequence.

1. **Inspect the assignment and workspace — complete.** Reviewed the assignment, reference screen, starter project, and transcript dataset.
2. **Agree on architecture and database structure — complete.** React + Vite, FastAPI, Supabase PostgreSQL, and Gemini; the initial `calls` and `call_stages` schema is applied to Supabase.
3. **Build the first persistence slice — backend implemented, partly verified.** Create/list calls were manually checked. Stage save/update, retrieve/resume, and close need a complete manual workflow check.
4. **Build all eight stages and reliable persistence — in progress.** The API accepts stages 1–8. The React/Vite scaffold exists, but stage guidance and call/history screens remain to be implemented.
5. **Implement Gemini assistance — not started.** Keep suggestions optional, include uncertainty, and provide a useful fallback.
6. **Analyze transcripts and refine guidance — not started.** Preserve original outcome labels and label inferences separately.
7. **Test the complete workflow — not started.**
8. **Deploy backend, frontend, and database configuration — not started.**
9. **Complete documentation and walkthrough preparation — in progress.** Setup and progress notes are documented; the walkthrough script remains to be prepared.

## Decisions to preserve

- A call can end at any stage.
- `calls.last_stage` records the furthest stage reached; `call_stages` contains each saved stage response.
- `original_outcome` preserves a source label. Do not convert `not_logged` into `not_interested`.
- Inferred outcomes remain separate from original labels and carry uncertainty.
- Supabase and Gemini secrets stay on the backend.
