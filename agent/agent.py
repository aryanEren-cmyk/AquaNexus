import os
import json
from dotenv import load_dotenv
from groq import Groq
from tools import (
    get_current_data,
    get_historical_baseline,
    calculate_anomaly,
    check_significance,
    get_spatial_pattern,
)

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

TOOLS_MAP = {
    "get_current_data": get_current_data,
    "get_historical_baseline": get_historical_baseline,
    "calculate_anomaly": calculate_anomaly,
    "check_significance": check_significance,
    "get_spatial_pattern": get_spatial_pattern,
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_data",
            "description": "Get recent measurements for a region/parameter",
            "parameters": {
                "type": "object",
                "properties": {
                    "region": {"type": "string"},
                    "parameter": {"type": "string"},
                    "time_range": {"type": "string"},
                },
                "required": ["region", "parameter", "time_range"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_historical_baseline",
            "description": "Get historical average for comparison",
            "parameters": {
                "type": "object",
                "properties": {
                    "region": {"type": "string"},
                    "parameter": {"type": "string"},
                    "period": {"type": "string"},
                },
                "required": ["region", "parameter", "period"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_anomaly",
            "description": "Calculate deviation between current value and historical baseline",
            "parameters": {
                "type": "object",
                "properties": {
                    "current_value": {"type": "number"},
                    "baseline_mean": {"type": "number"},
                },
                "required": ["current_value", "baseline_mean"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_significance",
            "description": "Check if an anomaly is significant using a threshold heuristic (not a formal statistical test)",
            "parameters": {
                "type": "object",
                "properties": {
                    "anomaly_deviation": {"type": "number"},
                    "std_dev": {"type": "number"},
                },
                "required": ["anomaly_deviation", "std_dev"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_spatial_pattern",
            "description": "Compare anomaly across nearby regions",
            "parameters": {
                "type": "object",
                "properties": {
                    "region": {"type": "string"},
                    "radius": {"type": "string"},
                },
                "required": ["region"],
            },
        },
    },
]

SYSTEM_PROMPT = (
    "You are AquaNexus, an ocean data analysis agent. When asked about "
    "conditions in a region, investigate using your tools: get current data, "
    "compare to historical baseline, calculate anomaly, check significance, "
    "and look at spatial patterns if useful. Then explain your findings "
    "clearly in plain language. Never claim this is a formal statistical "
    "significance test — call it a threshold-based heuristic. "
    "IMPORTANT: Respond in plain conversational text only. Do NOT use "
    "Markdown formatting — no asterisks, no bold, no headers (###), "
    "no bullet points, no horizontal rules (---). Write as if speaking "
    "naturally, using plain sentences and paragraphs."
)

def run_agent(message: str, history: list = None) -> dict:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.append({"role": "user", "content": message})

    # Agent loop — keep calling tools until the model gives a final text answer
    for _ in range(8):  # safety limit on loop iterations
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=TOOL_SCHEMAS,
            tool_choice="auto",
        )

        choice = response.choices[0].message

        if choice.tool_calls:
            messages.append(choice)
            for tool_call in choice.tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)
                result = TOOLS_MAP[fn_name](**fn_args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result),
                })
        else:
            return {
                "text": choice.content,
                "chart_data": None,
                "map_data": None,
            }

    return {"text": "I wasn't able to complete the analysis. Please try again.", "chart_data": None, "map_data": None}