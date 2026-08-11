import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from tools import (
    get_current_data,
    get_historical_baseline,
    calculate_anomaly,
    check_significance,
    get_spatial_pattern,
)

import os
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(
    "gemini-3.6-flash",
    tools=[
        get_current_data,
        get_historical_baseline,
        calculate_anomaly,
        check_significance,
        get_spatial_pattern,
    ],
)

def run_agent(message: str, history: list = None) -> dict:
    """
    Runs the agent on a user message, returns final response.
    history: list of {role, text} from previous turns (optional for now).
    """
    chat = model.start_chat(enable_automatic_function_calling=True)

    system_context = (
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

    response = chat.send_message(f"{system_context}\n\nUser question: {message}")

    return {
        "text": response.text,
        "chart_data": None,  # wired up in a later step
        "map_data": None,
    }