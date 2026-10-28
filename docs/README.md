# Module 1 project notes

Module 1 is complete. The deployed application provides a call guide, Supabase persistence, call history, and optional backend-generated response suggestions.

## Delivered

- The assignment's existing eight-stage call flow, with no additional stages.
- Call creation, stage save and update, resume, history, and completion at any stage.
- Caller-selected outcomes, end time, and duration.
- Optional suggestions using current prospect words and previously saved stages. The response includes likely intent and stage, uncertainty, three possible replies, and a next action. The caller remains in control.
- Supabase-backed storage with backend-only credentials and Render/Vercel deployment.

## Verification completed

- All 17 backend unit tests passed.
- Frontend ESLint and production build passed.
- Three live scenarios were checked in the deployed app: a callback request, a provider/price concern, and a do-not-call request. Each was assigned the expected intent and received an appropriate suggestion set.
- The live UI labeled those scenario results as fallback suggestions with high uncertainty. The QA call was closed with a do-not-call outcome.

See the [root README](../README.md) for the application overview and [transcript analysis](transcript-analysis.md) for aggregate dataset observations and prompt decisions.

## Decisions

- A call can end at any stage.
- `calls.last_stage` records the furthest stage reached; `call_stages` stores each saved stage response.
- `original_outcome` preserves a source label. Do not convert `not_logged` into `not_interested`.
- Inferred outcomes remain separate from original labels and carry uncertainty.
- Supabase and Gemini secrets stay on the backend.
