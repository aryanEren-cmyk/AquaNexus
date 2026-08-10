---
applyTo: "frontend/**"
---
# Frontend Context

Stack: React + Vite
Purpose: Chat interface where user asks natural-language questions about ocean data

## Key UI pieces
- Chat window (message bubbles, user + AI)
- Plotly charts (temperature/depth profiles, anomaly comparisons)
- Leaflet map (float locations, spatial pattern regions)
- Loading/thinking state — since agent takes multiple steps, show progress
  (e.g. "Checking historical data...", "Calculating anomaly...") not just a spinner

## Backend API contract
POST /chat
  Request:  { "message": string }
  Response: { "text": string, "chart_data": object | null, "map_data": object | null }

Base URL: http://localhost:8000

Production:
Use the deployed Render backend URL.