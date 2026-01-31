"""FastAPI service for the AQUA/Plan Democracia subagent."""
from __future__ import annotations

import asyncio
from uuid import uuid4

from fastapi import FastAPI, HTTPException

from .config import get_settings
from .gemini_client import GeminiError, generate_answer
from .schemas import ChatRequest, ChatResponse, HealthResponse

settings = get_settings()
app = FastAPI(title="AQUA – Plan Democracia", version="0.1.0")


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    message = (payload.message or "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="'message' es obligatorio")

    session_id = payload.session_id or str(uuid4())

    api_key = settings.gemini_api_key
    if settings.debug and payload.gemini_api_key:
        api_key = payload.gemini_api_key

    if not api_key:
        raise HTTPException(status_code=500, detail="Gemini API key no configurada")

    try:
        answer = await asyncio.to_thread(
            generate_answer,
            message,
            api_key=api_key,
            model=settings.gemini_model,
        )
    except GeminiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return ChatResponse(session_id=session_id, answer=answer)


# Nota: ejecutar con
# uvicorn agents.aqua.subagents.plan_democracia.api.main:app --host 0.0.0.0 --port 14001
