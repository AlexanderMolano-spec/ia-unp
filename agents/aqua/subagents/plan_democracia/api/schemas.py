"""Pydantic models for the plan_democracia API."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., description="Mensaje del analista o agente IA")
    input_mode: str = Field(..., description="Modo de entrada: text o voice")
    user: Optional[dict] = Field(
        None,
        description="Payload libre con información del usuario (region, roles, etc)",
    )


class AttachmentPayload(BaseModel):
    chartData: dict = Field(default_factory=dict)
    snippets: dict = Field(default_factory=dict)


class ChatResponse(BaseModel):
    outMode: str = Field(..., alias="outMode")
    text: str
    attachment: AttachmentPayload

    class Config:
        populate_by_name = True


class HealthResponse(BaseModel):
    status: str


__all__ = [
    "ChatRequest",
    "ChatResponse",
    "AttachmentPayload",
    "HealthResponse",
]
