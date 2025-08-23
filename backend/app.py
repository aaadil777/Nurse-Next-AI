# backend/app.py

import os
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

from guardrails import (
    needs_emergency_escalation,
    needs_refusal,
    EMERGENCY_MSG,
    REFUSAL_MSG,
)
from prompts import SYSTEM_PROMPT

# ---------- Env & client ----------
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or ""
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY missing. Put it in .env or environment variables.")

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

client = OpenAI(api_key=OPENAI_API_KEY)

# ---------- App ----------
app = FastAPI(title="AI Nurse Bot (Educational)", version="1.0.0")

# Allow local dev UIs (Streamlit, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Schemas ----------
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

class ChatResponse(BaseModel):
    role: str = "assistant"
    content: str

# ---------- Routes ----------
@app.get("/")
def root():
    return {"status": "ok", "service": "ai-nurse-bot", "docs": "/docs", "model": MODEL}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # Use the last user message for triage checks
    user_text = ""
    for m in reversed(req.messages):
        if m.role == "user":
            user_text = (m.content or "")[:4000]
            break

    if needs_emergency_escalation(user_text):
        return ChatResponse(content=EMERGENCY_MSG)

    if needs_refusal(user_text):
        return ChatResponse(content=REFUSAL_MSG)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + [
        {"role": m.role, "content": m.content} for m in req.messages
    ]

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.2,
        )
        content = resp.choices[0].message.content
    except Exception as e:
        content = f"Upstream model error: {e}"

    return ChatResponse(content=content)
