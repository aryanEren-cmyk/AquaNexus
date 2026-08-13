import json

from config import get_chat_provider, get_llm_config
from tools import (
    calculate_anomaly,
    calculate_profile_statistics,
    calculate_temperature_gradient,
    check_significance,
    detect_thermocline,
    get_current_data,
    get_historical_baseline,
    get_profile,
    get_spatial_pattern,
    get_temperature_at_depth,
)


TOOLS_MAP = {
    "get_current_data": get_current_data,
    "get_historical_baseline": get_historical_baseline,
    "calculate_anomaly": calculate_anomaly,
    "check_significance": check_significance,
    "get_spatial_pattern": get_spatial_pattern,
    "get_profile": get_profile,
    "get_temperature_at_depth": get_temperature_at_depth,
    "calculate_temperature_gradient": calculate_temperature_gradient,
    "calculate_profile_statistics": calculate_profile_statistics,
    "detect_thermocline": detect_thermocline,
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
            "description": "Check if an anomaly is significant using a threshold heuristic",
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
    {
        "type": "function",
        "function": {
            "name": "get_profile",
            "description": "Get one complete synthetic/test ocean profile by ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "profile_id": {"type": "string"},
                },
                "required": ["profile_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_temperature_at_depth",
            "description": "Get deterministic temperature at a requested depth for a synthetic/test profile",
            "parameters": {
                "type": "object",
                "properties": {
                    "profile_id": {"type": "string"},
                    "target_depth": {"type": "number"},
                },
                "required": ["profile_id", "target_depth"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_temperature_gradient",
            "description": "Calculate segment-by-segment temperature gradients for a synthetic/test profile",
            "parameters": {
                "type": "object",
                "properties": {
                    "profile_id": {"type": "string"},
                },
                "required": ["profile_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_profile_statistics",
            "description": "Calculate deterministic summary statistics for a synthetic/test profile",
            "parameters": {
                "type": "object",
                "properties": {
                    "profile_id": {"type": "string"},
                },
                "required": ["profile_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "detect_thermocline",
            "description": "Detect the strongest temperature-gradient zone using a simplified heuristic",
            "parameters": {
                "type": "object",
                "properties": {
                    "profile_id": {"type": "string"},
                },
                "required": ["profile_id"],
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
    "significance test; call it a threshold-based heuristic. "
    "IMPORTANT: Respond in plain conversational text only. Do NOT use "
    "Markdown formatting: no asterisks, no bold, no headers, no bullet "
    "points, and no horizontal rules. Write as if speaking naturally, "
    "using plain sentences and paragraphs."
)


def _format_response(text: str) -> dict:
    return {
        "text": text,
        "chart_data": None,
        "map_data": None,
    }


def run_agent(message: str, history: list = None, chat_provider=None) -> dict:
    config = get_llm_config()
    provider = chat_provider or get_chat_provider(config)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.append({"role": "user", "content": message})

    for _ in range(config.max_tool_calls):
        response = provider.create_completion(
            messages=messages,
            tools=TOOL_SCHEMAS,
        )

        choice = response.choices[0].message

        if choice.tool_calls:
            messages.append(choice)
            for tool_call in choice.tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)
                result = TOOLS_MAP[fn_name](**fn_args)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result),
                    }
                )
        else:
            return _format_response(choice.content)

    return _format_response("I wasn't able to complete the analysis. Please try again.")
