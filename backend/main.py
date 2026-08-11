import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "agent"))
from agent import run_agent

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    text: str
    chart_data: Optional[dict] = None
    map_data: Optional[dict] = None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        result = run_agent(request.message)
        return ChatResponse(**result)
    except Exception as e:
        return ChatResponse(text=f"Something went wrong: {str(e)}")