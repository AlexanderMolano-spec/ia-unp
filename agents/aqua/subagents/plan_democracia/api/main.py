"""FastAPI service for the AQUA/Plan Democracia subagent."""
from __future__ import annotations

import asyncio
from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException, Response
from fastapi.responses import JSONResponse

from agents.shared.llm.config import get_settings
from agents.shared.llm.gemini_client import GeminiError, generate_answer
from .schemas import (
    AttachmentPayload,
    ChatRequest,
    ChatResponse,
    HealthResponse,
)

settings = get_settings()
app = FastAPI(title="AQUA – Plan Democracia", version="0.1.0")


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    response: Response,
    x_user_id: str = Header(..., alias="X-User-Id"),
    x_session_id: str | None = Header(None, alias="X-Session-Id"),
    gemini_api_key_header: str | None = Header(None, alias="GEMINI_API_KEY"),
) -> ChatResponse:
    message = (payload.message or "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="'message' es obligatorio")

    input_mode = (payload.input_mode or "text").strip().lower()
    if input_mode not in {"text", "voice"}:
        raise HTTPException(status_code=400, detail="'input_mode' inválido")

    session_id = x_session_id or str(uuid4())

    api_key = settings.gemini_api_key
    if settings.debug:
        if gemini_api_key_header:
            api_key = gemini_api_key_header
        else:
            raise HTTPException(
                status_code=400,
                detail="GEMINI_API_KEY requerido en modo DEBUG",
            )

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

    response.headers["X-Session-Id"] = session_id

    attachment = AttachmentPayload(chartData={}, snippets={})
    return ChatResponse(
        outMode=input_mode,
        text=answer,
        attachment=attachment,
    )


# Nota: ejecutar con
# uvicorn agents.aqua.subagents.plan_democracia.api.main:app --host 0.0.0.0 --port 14001
