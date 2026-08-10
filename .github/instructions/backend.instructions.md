---
applyTo: "backend/**"
---
# Backend Context

Stack: FastAPI (Python)
Purpose: Receives chat requests from frontend, calls agent, returns structured response

## Database
PostgreSQL + PostGIS via Supabase (free tier)
Core tables: floats, profiles, measurements, parameters
(measurements links profiles + parameters, stores value + quality control flag)

## Main endpoint
POST /chat
  Request:  { "message": string , "session_id": string}
  Response: { "text": string, "chart_data": object | null, "map_data": object | null }

This endpoint calls the agent (agent/ folder) and formats its output for the frontend.

## Data rules
- Only use measurements where quality control flag = valid/good
- Never expose raw DB errors to frontend — catch and return clean error messages