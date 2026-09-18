"""Combines all v1 route routers into a single APIRouter."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.routes import analysis, chat, documents

api_router = APIRouter()

api_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["Documents"],
)
api_router.include_router(
    analysis.router,
    prefix="/analysis",
    tags=["Analysis"],
)
api_router.include_router(
    chat.router,
    prefix="/chat",
    tags=["Chat"],
)
