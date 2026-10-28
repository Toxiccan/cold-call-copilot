# Project notes and completion stages

The project overview and current milestone status are maintained in the [root README](../README.md). This file records the implementation sequence.

Aggregate transcript observations and prompt decisions are in [transcript analysis notes](transcript-analysis.md). The source transcript bundle remains local and is not published.

1. **Inspect the assignment and workspace — complete.** Reviewed the assignment, reference screen, starter project, and transcript dataset.
2. **Agree on architecture and database structure — complete.** React + Vite, FastAPI, Supabase PostgreSQL, and Gemini; the initial `calls` and `call_stages` schema is applied to Supabase.
3. **Build the first persistence slice — backend implemented, partly verified.** Create/list calls were manually checked. Stage save/update, retrieve/resume, and close need a complete manual workflow check.
4. **Build the reference-inspired call screens — implemented; local verification pending.** The active-call and history views are wired to the backend API. Use the assignment’s existing eight-stage flow, and ground response examples in the supplied transcripts without adding stages or unsupported prompts.
5. **Implement Gemini assistance — implemented; live verification pending.** The backend analyzes the current prospect words and earlier saved stages, returns optional suggestions with uncertainty, and provides a local fallback. It never advances or closes a call.
6. **Analyze transcripts and refine guidance — in progress.** Source metadata and call endings are reviewed. Gemini receives transcript-informed intent labels and paraphrased stage patterns. A 12-case synthetic evaluation set is available; validated stage annotations and live model evaluation remain. Preserve source outcome labels and keep inferences separate.
7. **Test the complete workflow — not started.**
8. **Deploy backend, frontend, and database configuration — not started.**
9. **Complete documentation and walkthrough preparation — in progress.** Setup and progress notes are documented; the walkthrough script remains to be prepared.

## Decisions to preserve

- A call can end at any stage.
- `calls.last_stage` records the furthest stage reached; `call_stages` contains each saved stage response.
- `original_outcome` preserves a source label. Do not convert `not_logged` into `not_interested`.
- Inferred outcomes remain separate from original labels and carry uncertainty.
- Supabase and Gemini secrets stay on the backend.
