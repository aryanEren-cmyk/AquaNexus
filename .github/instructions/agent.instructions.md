---
applyTo: "agent/**"
---
# Agent / RAG Context

LLM: Gemini API (free tier) — primary. Groq — backup if rate-limited.
Vector DB: ChromaDB (local, for RAG on Argo documentation/manuals)
Approach: raw function/tool-calling (NOT LangChain/LangGraph)

## Tool functions (the agent decides which to call, in what order)
- get_current_data(region, parameter, time_range) → recent measurements
- get_historical_baseline(region, parameter, period) → historical average for comparison
- calculate_anomaly(current, baseline) → deviation and percentage deviation
- check_significance(anomaly, std_dev) → bool, using threshold rule:
  significant if abs(anomaly) > 1.5 standard deviations from historical mean
  (NOT a real statistical test — deliberately simplified for reliability)
- get_spatial_pattern(region, radius) → comparison across 3-5 nearby regions
- generate_explanation(all_above) → LLM call producing plain-language summary,
  citing what was checked

## Example flow
User: "Is the Arabian Sea getting unusually warm?"
1. get_current_data("Arabian Sea", "temperature", "recent")
2. get_historical_baseline("Arabian Sea", "temperature", "5yr avg same month")
3. calculate_anomaly(current, baseline) → deviation and percentage deviation
4. check_significance(anomaly, std_dev)
5. get_spatial_pattern("Arabian Sea", radius)
6. generate_explanation(all results) → returned as final text response