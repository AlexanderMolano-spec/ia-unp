"""Pydantic models for the plan_democracia API."""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., description="Mensaje del analista o agente IA")
    session_id: Optional[str] = Field(
        None, description="Identificador lógico de la sesión del subagente"
    )
    user_id: Optional[str] = Field(
        None, description="Identificador del usuario solicitante (opcional)"
    )
    gemini_api_key: Optional[str] = Field(
        None,
        description="Solo en DEBUG. Permite probar con claves temporales",
    )


class ChatResponse(BaseModel):
    session_id: str
    answer: str


class HealthResponse(BaseModel):
    status: str


__all__ = ["ChatRequest", "ChatResponse", "HealthResponse"]
