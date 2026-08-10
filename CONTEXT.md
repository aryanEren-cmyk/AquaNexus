# AquaNexus — Shared Project Context

## 1. Project Overview

AquaNexus is an AI-powered interface for exploring and reasoning over
oceanographic ARGO float data.

Users ask natural-language questions such as:

> Is the Arabian Sea getting unusually warm?

AquaNexus should retrieve relevant ocean data, compare it with historical
behavior, perform analysis, and explain the result in plain language.

The core differentiator is an **agentic reasoning chain**, not a basic
LLM chatbot.

---

## 2. Core User Flow

The guaranteed demo path is:

User question
    ↓
React frontend
    ↓
POST /chat
    ↓
FastAPI backend
    ↓
AI agent
    ↓
Tool calls
    ↓
ARGO database / RAG
    ↓
Analysis
    ↓
Natural-language explanation
    ↓
Structured response
    ↓
Frontend visualization

This typed-input → agent → response path must always work.

OCR and visual polish are optional layers and must never block the core flow.

---

## 3. System Architecture

```text
┌─────────────────────┐
│     React / Vite    │
│      Frontend       │
└──────────┬──────────┘
           │
        POST /chat
           │
           ▼
┌─────────────────────┐
│       FastAPI       │
│       Backend       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│     AI Agent / LLM  │
│    Tool Calling     │
└───────┬───────┬─────┘
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



 Responsibilities

Frontend

User interaction
Chat interface
Loading/progress states
Charts
Maps

Backend

API layer
Agent orchestration boundary
Database access/configuration
Stable response contract

Agent

Understand user intent
Decide which tools are required
Chain tool calls
Analyze results
Generate explanation

Database

Store and query ARGO observations

RAG

Answer domain/reference questions from trusted documents
Must not replace database queries for actual measurements
4. Technology Stack
Frontend
React
Vite
Plotly for charts
Leaflet for maps
Backend
Python
FastAPI
Agent
Python
Gemini or Groq
Native function/tool calling
Database
Supabase
PostgreSQL
PostGIS
RAG
ChromaDB
Embeddings
Deployment
Frontend: Vercel
Backend: Render

Use the simplest implementation that satisfies the requirements.
Do not introduce unnecessary libraries or infrastructure

5. Agent Tools

The initial agent tool set is:

get_current_data(region, parameter, time_range)

get_historical_baseline(region, parameter, period)

calculate_anomaly(current, baseline)

check_significance(anomaly, std_dev)

get_spatial_pattern(region, radius)

generate_explanation(all_results)
Tool requirements
Each tool must have a clear purpose.
Each tool must have explicit inputs and outputs.
Tools must be independently testable.
Keep tool functions small.
Keep public function signatures stable.
Initially, tools may use mock data.
Mock implementations will later be replaced with real database queries.

The agent should choose tools based on the question rather than blindly
calling every tool for every request.

Example:

"Is the Arabian Sea getting unusually warm?"

→ current data
→ historical baseline
→ anomaly
→ significance
→ spatial comparison (if useful)
→ explanation
6. Data & Analysis

AquaNexus will work with real ARGO ocean-float observations.

Important data includes:

Float ID
Location
Timestamp
Temperature
Salinity
Pressure
Quality-control information

For the hackathon, use a manageable and verified ARGO dataset rather than
attempting to ingest the entire global archive.

Anomaly

An anomaly represents the difference between an observed/current value and
its historical baseline.

Significance

For the MVP, use a simple threshold heuristic rather than claiming to perform
a formal statistical significance test.

A deviation greater than approximately 1.5 standard deviations from the
historical mean can be treated as notable.

The implementation should consider both positive and negative deviations.

Do NOT describe this heuristic as a rigorous statistical hypothesis test.

7. API Contract
POST /chat

Request:

{
  "message": "Is the Arabian Sea getting unusually warm?"
}

Response:

{
  "text": "The Arabian Sea is showing ...",
  "chart_data": null,
  "map_data": null
}
text

Final natural-language explanation.

chart_data

Structured data for frontend visualization.

Use null when a chart is unnecessary.

Example:

{
  "type": "line",
  "title": "Sea Temperature Trend",
  "x": ["2024-01", "2024-02", "2024-03"],
  "y": [28.1, 28.4, 29.0],
  "x_label": "Time",
  "y_label": "Temperature (°C)"
}
map_data

Structured geographic data.

Use null when a map is unnecessary.

Example:

{
  "type": "points",
  "points": [
    {
      "lat": 15.2,
      "lon": 68.4,
      "label": "Float 2901234"
    }
  ]
}

The backend owns this contract.

The frontend must not depend on internal agent/tool structures.

8. Engineering Rules
main must always remain working.
Use feature branches for development.
Never commit API keys or .env files.
Keep API contracts stable.
Test integration boundaries early.
Prefer simple solutions over over-engineering.
Mock dependencies when necessary, then replace mocks progressively.
Never fabricate scientific data or conclusions.
If a feature threatens the core demo path, deprioritize it.
Communicate breaking changes before implementing them.
9. Feature Priority
P0 — MUST WORK
React frontend
FastAPI backend
/chat
Agent
Tool calling
Real ARGO data
Database
Natural-language explanation
P1 — HIGH VALUE
Historical comparison
Anomaly detection
Spatial comparison
Charts
Maps
Domain RAG
P2 — POLISH
Agent progress states
Visual refinement
Animations
Responsive improvements
P3 — STRETCH
OCR
Additional advanced features

If P2/P3 work threatens P0 reliability, stop working on P2/P3.

