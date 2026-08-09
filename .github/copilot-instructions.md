# FloatChat AI — Project Context

## What we're building
AI-powered conversational interface for ARGO ocean data (SIH260521, Ministry of Earth Sciences).
Differentiator: agentic multi-step reasoning — the agent investigates (checks current data,
compares to historical baseline, checks significance, looks at spatial pattern) instead of
running a single SQL query like typical FloatChat builds.

## Team structure
- frontend/  → React + Vite chat UI (charts via Plotly, maps via Leaflet)
- backend/   → FastAPI, wraps agent logic + DB access, exposes REST API to frontend
- agent/     → RAG + tool-calling agent logic (the core differentiator)

## Global conventions
- Free-tier services ONLY: Gemini API / Groq (LLM), Supabase (Postgres+PostGIS),
  ChromaDB (local, vector DB), Vercel (frontend hosting), Render/Railway (backend hosting)
- Prefer simple, debuggable code over clever/complex abstractions — we're on a hackathon timeline
- No LangChain/LangGraph — use raw function/tool-calling directly against the LLM API
- All API responses: JSON, snake_case keys
- Never hardcode API keys — use environment variables (.env, gitignored)