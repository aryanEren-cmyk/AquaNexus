from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Allow frontend (running on a different port) to call this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this before deployment
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
    # Mock response for now — Step 4 will replace this with a real agent call
    return ChatResponse(
        text=f"[MOCK] You asked: '{request.message}'. Real agent reasoning coming in Step 4.",
        chart_data=None,
        map_data=None,
    )