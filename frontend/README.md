# Frontend

React + Vite frontend for the Cold Call Copilot. The active-call guide and call-history views use FastAPI for call creation, stage persistence, resume, outcome logging, and optional AI response suggestions. Suggestions come from backend Gemini when configured, otherwise from a local fallback. The full workflow still needs local verification.

## Local setup

From this `frontend` directory:

```powershell
npm install
npm run dev
```

Vite prints the local address to open in a browser. Available scripts are `npm run dev`, `npm run lint`, `npm run build`, and `npm run preview`.

The Vite development server proxies `/api` requests to `http://127.0.0.1:8000`, so run the FastAPI backend as well. For a deployed frontend, set `VITE_API_BASE_URL` to the backend's base URL.

## Phase 4 scope: reference-inspired call screens

- Start a call with a prospect and optional company name.
- Show the selected stage and progress through the assignment's existing eight-stage flow.
- Capture a response category, the prospect's exact words, and optional notes; save changes through FastAPI.
- Resume in-progress calls from history and inspect completed calls.
- End a call at any stage with a caller-selected outcome.
- Request optional response suggestions based on the current prospect words and earlier saved stages. The caller chooses what to say; the app never advances or closes the call automatically.
- Review the model's likely intent and stage, explanation, three possible replies, next action, and uncertainty. The result identifies whether it came from Gemini or the fallback.

Transcript-backed response examples are currently included for the Purpose stage. Examples for the other stages remain to be reviewed and added.

Do not put Supabase secret keys or Gemini API keys in frontend code. See the [project README](../README.md) for current milestone status.
