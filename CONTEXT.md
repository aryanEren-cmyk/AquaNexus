# AquaNexus — Shared Engineering Context

## 1. Project Overview

AquaNexus is an AI-powered interface for exploring and reasoning over oceanographic
ARGO float data (SIH260521, Ministry of Earth Sciences).

Users ask natural-language questions such as:

> Is the Arabian Sea getting unusually warm?

AquaNexus retrieves relevant ocean data, compares it with historical behavior,
performs analysis, and explains the result in plain language — supporting
natural follow-up questions within the same conversation.

The core differentiator is an **agentic reasoning chain**, not a basic
single-query LLM chatbot. Most existing solutions to this problem convert a
question into one database query and return an answer. AquaNexus investigates —
it decides what to check, compares against history, and explains what it found.

---

## 2. Core User Flow

The guaranteed demo path is:

```
User question
    ↓
React frontend (generates/reuses session_id)
    ↓
POST /chat  { message, session_id }
    ↓
FastAPI backend (retrieves conversation history for session_id)
    ↓
AI agent (receives message + recent history)
    ↓
Tool calls
    ↓
ARGO database / RAG
    ↓
Analysis
    ↓
Natural-language explanation
    ↓
Structured response  { text, chart_data, map_data }
    ↓
Frontend visualization
```

This typed-input → agent → response path must always work, including basic
multi-turn follow-ups. OCR and visual polish are optional layers and must
never block the core flow.

---

## 3. System Architecture

```
┌─────────────────────┐
│     React / Vite     │
│      Frontend         │
└──────────┬────────────┘
           │
        POST /chat
      { message, session_id }
           │
           ▼
┌─────────────────────┐
│       FastAPI         │
│       Backend         │
│ (session history store)│
└──────────┬────────────┘
           │
           ▼
┌─────────────────────┐
│   AI Agent / LLM      │
│   Tool Calling         │
│ (uses recent history)  │
└───────┬───────┬───────┘
        │       │
        ▼       ▼
┌────────────┐ ┌──────────────┐
│ Supabase   │ │   ChromaDB   │
│ PostgreSQL │ │     RAG      │
│ + PostGIS  │ │              │
└─────┬──────┘ └──────────────┘
      │
      ▼
 ARGO float data
```

---

## 4. Responsibilities

**Frontend**
- User interaction, chat interface
- Generates and persists `session_id` for the conversation
- Loading/progress states, error states
- Charts (Plotly), maps (Leaflet)

**Backend**
- API layer, stable response contract
- Maintains in-memory conversation history keyed by `session_id`
- Agent orchestration boundary
- Database access/configuration

**Agent**
- Understand user intent (including follow-up questions using conversation history)
- Decide which tools are required
- Chain tool calls
- Analyze results
- Generate explanation

**Database**
- Store and query real ARGO observations

**RAG**
- Answer domain/reference questions from trusted documents (Argo manuals, docs)
- Must NOT replace database queries for actual measurements

---

## 5. Technology Stack

| Layer | Choice |
|---|---|
| Frontend | React + Vite |
| Charts | Plotly |
| Maps | Leaflet |
| Backend | Python, FastAPI |
| Agent | Python, Gemini (primary) / Groq (backup), native function/tool calling — NOT LangChain/LangGraph |
| Database | Supabase — PostgreSQL + PostGIS |
| RAG | ChromaDB, embeddings |
| Deployment | Frontend → Vercel, Backend → Render/Railway |

All services free-tier only. Use the simplest implementation that satisfies
requirements — do not introduce unnecessary libraries or infrastructure.

---

## 6. Agent Tools

Initial tool set:

1. `get_current_data(region, parameter, time_range)` → recent measurements
2. `get_historical_baseline(region, parameter, period)` → historical average for comparison
3. `calculate_anomaly(current, baseline)` → deviation (absolute + percentage)
4. `check_significance(anomaly, std_dev)` → bool, using threshold rule:
   significant if `abs(anomaly) > 1.5` standard deviations from historical mean
   — **NOT a real statistical test**, deliberately simplified for hackathon
   reliability. Considers both positive (warming) and negative (cooling) deviations.
5. `get_spatial_pattern(region, radius)` → comparison across 3-5 nearby regions
6. `generate_explanation(all_results)` → LLM call producing plain-language
   summary, citing what was checked at each step

**Tool requirements:**
- Clear docstrings, explicit inputs/outputs
- Independently testable, no hidden global state
- Small, focused functions
- Stable public signatures — mock data now, real DB queries later, without
  changing the signature
- The agent chooses tools based on the question — it must NOT blindly call
  every tool for every request

**Example flow:**

User: "Is the Arabian Sea getting unusually warm?"
1. Identify region = Arabian Sea, parameter = temperature, time range = recent
2. `get_current_data("Arabian Sea", "temperature", "recent")`
3. `get_historical_baseline("Arabian Sea", "temperature", "5yr avg same month")`
4. `calculate_anomaly(current, baseline)`
5. `check_significance(anomaly, std_dev)`
6. `get_spatial_pattern("Arabian Sea", radius)` — if useful
7. `generate_explanation(all results)` → returned as final text response

---

## 7. Conversation Memory (Multi-Turn Support)

AquaNexus supports multi-turn conversations via `session_id`.

- **Frontend**: generates a `session_id` (UUID) when the chat window first
  loads, persists it in React state for that session, and sends it with
  every `/chat` request.
- **Backend**: maintains conversation history per `session_id`. In-memory
  storage (a simple dict) is sufficient for the hackathon — no persistent
  DB table required. Passes the last 3-4 turns of relevant history to the agent.
- **Agent**: receives recent conversation history alongside the current
  message, and uses it to resolve follow-up questions — e.g. "now show me
  last year" referring to the region/parameter established earlier in the
  conversation. Does not require full history, only the last few exchanges.

This is a **P1 feature** — high value, not required for the absolute minimum
demo path. If time runs short, the system can fall back to single-turn
behavior without changing the core agent logic (only the history parameter
would be empty/unused).

---

## 8. Data & Analysis

AquaNexus works with real ARGO ocean-float observations.

**Important data fields:** Float ID, location (lat/lon), timestamp,
temperature, salinity, pressure, quality-control flag.

For the hackathon, use a manageable, verified ARGO dataset rather than
attempting to ingest the entire global archive. The data source must be
documented for judge questions.

**Anomaly:** the difference between an observed/current value and its
historical baseline (absolute + percentage deviation).

**Significance:** a simple threshold heuristic (>1.5 SD, either direction),
NOT a formal statistical hypothesis test. Never describe it to judges as
rigorous statistical significance testing — describe it as a heuristic
threshold used to flag notable deviations.

---

## 9. Database Responsibilities

Core tables (design around what the agent actually needs — no unnecessary tables):
- `floats` — float metadata
- `profiles` — float/profile information, geographic coordinates, timestamps
- `measurements` — links profiles + parameters, stores value + quality-control flag
- `parameters` — parameter definitions (temperature, salinity, pressure)

Use PostGIS for geographic/spatial operations (float locations, spatial
pattern comparisons).

Only use measurements where the quality-control flag = valid/good.

---

## 10. Data Ingestion

ARGO data arrives in NetCDF format. Ingestion pipeline should:
1. Read the selected ARGO sample
2. Validate required fields
3. Convert to the database schema
4. Preserve timestamps, coordinates, and quality-control information
5. Insert usable records into PostgreSQL

Prioritize a manageable, verified dataset over attempting full-archive ingestion.

---

## 11. API Contract

**POST /chat**

Request:
```json
{
  "message": "Is the Arabian Sea getting unusually warm?",
  "session_id": "abc123"
}
```

Response:
```json
{
  "text": "The Arabian Sea is showing ...",
  "chart_data": null,
  "map_data": null
}
```

- `text` — human-readable final answer
- `chart_data` — structured chart info, or `null` if no chart is needed

```json
{
  "type": "line",
  "title": "Sea Temperature Trend",
  "x": ["2024-01", "2024-02", "2024-03"],
  "y": [28.1, 28.4, 29.0],
  "x_label": "Time",
  "y_label": "Temperature (°C)"
}
```

- `map_data` — structured geographic info, or `null` if no map is needed

```json
{
  "type": "points",
  "points": [
    { "lat": 15.2, "lon": 68.4, "label": "Float 2901234" }
  ]
}
```

The backend owns this contract. The frontend must never depend on internal
agent/tool structures, and the agent must never send arbitrary
frontend-specific objects directly.

**GET /health**

Response:
```json
{ "status": "ok" }
```
Used for deployment and integration testing.

---

## 12. Error Handling

The system must fail gracefully. Possible failures include: invalid region,
no available data, missing historical baseline, database failure, LLM
failure, tool failure, LLM rate limit, invalid tool arguments, slow external
service.

Rules:
- The user must receive a useful, clear error message
- Never silently return fabricated scientific results
- Never crash the entire application because an optional tool failed
- Never expose raw DB errors to the frontend — catch and return clean messages

---

## 13. RAG Responsibilities

RAG is for domain knowledge that should not be guessed by the LLM — e.g.
ARGO documentation, float manuals, technical/oceanographic reference material.

Process: retrieve relevant chunks → provide to the LLM → generate an answer
grounded in those documents → cite/identify the source where appropriate.

RAG should never replace database queries for actual ocean measurements.
- **Database** → quantitative observational data
- **RAG** → domain/reference knowledge

---

## 14. Frontend Responsibilities

**Required:** message list, input field, send button, loading state, error
state, assistant response, chart rendering when `chart_data` exists, map
rendering when `map_data` exists, `session_id` generation/persistence.

**Optional:** agent progress states, animations, advanced visual polish, OCR upload.

The frontend must handle `chart_data = null` and `map_data = null` without
rendering broken or empty components.

---

## 15. Agent Progress UI

When possible, communicate meaningful agent stages to the user, e.g.:
"Understanding question...", "Retrieving current observations...",
"Checking historical baseline...", "Calculating anomaly...",
"Comparing nearby regions...", "Preparing explanation..."

If backend streaming isn't implemented, simulated progress states are
acceptable for the hackathon. Do not build complicated streaming
infrastructure unless it clearly improves the demo and can be done safely.

---

## 16. OCR (Stretch Feature)

OCR is P3 — a stretch feature only.

```
Image → POST /ocr → OCR extraction → Extracted text → User edits text → POST /chat
```

OCR must never become a dependency of the primary chat path. If it becomes
unreliable or starts consuming significant development time, remove it
from the demo entirely.

---

## 17. Security

**Never commit:** API keys, `.env`, passwords, database credentials,
service-account secrets.

Use environment variables. `.env` must be in `.gitignore`. Public frontend
code must never contain private backend/database credentials.

---

## 18. Git Rules

- `main` must always remain deployable
- Never push experimental/broken work directly to `main`
- Use feature branches: `feature/frontend-chat`, `feature/backend-api`,
  `feature/agent-tools`, `feature/data-ingestion`, `feature/rag`, `feature/ocr`
- Make small commits, merge only tested changes
- If a change breaks another teammate's work, communicate immediately

---

## 19. Engineering Rules

1. Prefer simple implementations over clever ones
2. Do not introduce a library unless it solves a real problem
3. Do not duplicate business logic across frontend and backend
4. Keep agent tools small and independently testable
5. Keep API contracts stable
6. Do not hardcode fake scientific claims
7. Mock first when dependencies are not ready
8. Replace mocks with real implementations progressively
9. Test every integration boundary
10. Optimize for a reliable demo before adding features

---

## 20. Priority System

**P0 — MUST WORK**
React frontend · `/chat` · Agent · Tool calling · Real ARGO data · Database ·
Natural-language explanation

**P1 — HIGH VALUE**
Historical baseline · Anomaly detection · Spatial comparison · Chart · Map ·
Domain RAG · Multi-turn conversation memory

**P2 — POLISH**
Agent progress UI · Better visual design · Animations · Responsive layout ·
Better error messages

**P3 — STRETCH**
OCR · Additional advanced capabilities

If a P2/P3 feature threatens P0 reliability, stop working on it. If P1
(including multi-turn memory) threatens P0, fall back gracefully — the
system should still work single-turn if needed.

---

## 21. Demo Philosophy

The judge should understand the product within seconds. The ideal
demonstration:

1. User asks a natural-language ocean question
2. AquaNexus visibly reasons through the required analysis
3. Real ARGO observations are retrieved
4. Current conditions are compared with historical behavior
5. An anomaly is identified
6. Spatial context is shown
7. A chart/map supports the explanation
8. The agent explains the result clearly
9. (If time allows) a natural follow-up question is understood in context

The demo should feel like: **"Ask a question about the ocean → AquaNexus
investigates the data → AquaNexus explains what it found."**

Not: "Here is a chatbot that calls an LLM."

---

## 22. Non-Goals

For the hackathon MVP, do NOT attempt:
- Full global ARGO ingestion
- Production-grade statistical modeling
- Complex ML forecasting
- Custom foundation models
- Over-engineered microservices
- Complex authentication
- Large-scale distributed infrastructure
- Real-time ocean simulation
- Dozens of unrelated AI features
- Long-term persistent conversation storage (in-memory is enough)

The goal is a reliable, technically credible prototype.

---

## 23. Current Development State

**Status: PROJECT JUST STARTED.** Nothing should be assumed to be implemented.

Current repository structure:
```
AQUANEXUS/
├── .git/
├── .github/
│   ├── copilot-instructions.md
│   └── instructions/
│       ├── agent.instructions.md
│       ├── backend.instructions.md
│       └── frontend.instructions.md
├── agent/
├── backend/
├── data/
├── docs/
├── frontend/
├── README.md
└── CONTEXT.md
```

---

## 24. Source of Truth

This file defines the shared architecture and contracts. If an
implementation decision conflicts with this document:
1. Stop.
2. Identify the conflict.
3. Discuss the change.
4. Update this document if the architecture genuinely needs to change.

Do not silently create incompatible implementations. Keep this file, and
the three `.github/instructions/*.instructions.md` files, in sync at all times.

---

## 25. Current Milestone

**FIRST MILESTONE — smallest complete vertical slice:**

```
React (generates session_id)
    ↓
POST /chat { message, session_id }
    ↓
FastAPI
    ↓
Agent (mock tools, ignores history for now)
    ↓
Agent response
    ↓
React (displays response)
```

Only after this vertical slice works should the team progressively introduce,
in order:

```
Mock data → Real database → Real ARGO data → Analysis (anomaly/significance)
→ RAG → Conversation memory (multi-turn) → Charts → Maps → Polish
```

The application should always have a working end-to-end path at every stage.