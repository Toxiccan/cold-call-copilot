# Frontend

React + Vite frontend for the Cold Call Copilot. The current files are the Vite React starter scaffold; the call guide, history screen, and backend integration still need to be built.

## Local setup

From this `frontend` directory:

```powershell
npm install
npm run dev
```

Vite prints the local address to open in a browser. Available scripts are `npm run dev`, `npm run lint`, `npm run build`, and `npm run preview`.

## Planned caller workflow

- Show the current stage, its purpose, common prospect responses, and progress through eight stages.
- Capture a response category, the prospect's exact words, and optional notes.
- Save through FastAPI so a call can be resumed after a refresh.
- Allow navigation between stages and call closure with an outcome at any point.
- Show past calls with status, duration, last stage, and outcome.

The frontend must call FastAPI for persistence. Do not put Supabase secret keys or Gemini API keys in frontend code. See the [project README](../README.md) for current milestone status.
