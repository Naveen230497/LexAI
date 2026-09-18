"""Async wrapper around the Google Gemini generative AI SDK."""

from __future__ import annotations

import asyncio
import json
import re
from typing import AsyncGenerator
import logging

import google.generativeai as genai

logger = logging.getLogger(__name__)


class GeminiClient:
    """Isolated wrapper around the Google Gemini API with fallback support.

    Keeping Gemini calls isolated in this class makes the client trivially
    mockable in tests — replace this single class to avoid any real API calls
    during the test suite.

    Attributes:
        _model: Configured ``GenerativeModel`` instance (Primary).
        _fallback_model: Configured ``GenerativeModel`` instance (Fallback).
        _embedding_model: Name of the Gemini embedding model.
    """

    def __init__(self, api_key: str, model: str, embedding_model: str) -> None:
        # Security: API key is passed explicitly and never stored in a global
        # variable so it does not leak through module-level introspection.
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(model)
        # Configure a highly available fallback model for reliability
        self._fallback_model = genai.GenerativeModel("gemini-2.5-flash-lite")
        self._embedding_model = embedding_model

    async def generate(self, prompt: str) -> str:
        try:
            response = await asyncio.to_thread(self._model.generate_content, prompt)
        except Exception as exc:
            logger.warning("Primary model failed: %s. Using fallback.", exc)
            response = await asyncio.to_thread(self._fallback_model.generate_content, prompt)
            
        if not response.text:
            raise RuntimeError("Gemini returned an empty or blocked response.")
        return response.text

    async def generate_json(self, prompt: str) -> dict:
        raw = await self.generate(prompt)
        cleaned = _strip_code_fences(raw)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Gemini returned invalid JSON: {exc}\nRaw response:\n{raw[:500]}"
            ) from exc

    async def stream_generate(self, prompt: str) -> AsyncGenerator[str, None]:
        def _stream_sync(model: genai.GenerativeModel) -> list[str]:
            chunks: list[str] = []
            for chunk in model.generate_content(prompt, stream=True):
                if chunk.text:
                    chunks.append(chunk.text)
            return chunks

        try:
            tokens = await asyncio.to_thread(_stream_sync, self._model)
        except Exception as exc:
            logger.warning("Primary model streaming failed: %s. Using fallback.", exc)
            tokens = await asyncio.to_thread(_stream_sync, self._fallback_model)
            
        for token in tokens:
            yield token

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        result = genai.embed_content(
            model=self._embedding_model,
            content=texts,
            task_type="retrieval_document",
        )
        return result["embedding"]


def _strip_code_fences(text: str) -> str:
    text = text.strip()
    pattern = re.compile(r"^```(?:json)?\s*(.*?)\s*```$", re.DOTALL)
    match = pattern.match(text)
    if match:
        return match.group(1)
    return text


def get_gemini_client() -> GeminiClient:
    from app.config import get_settings

    settings = get_settings()
    return GeminiClient(
        api_key=settings.GEMINI_API_KEY,
        model=settings.GEMINI_MODEL,
        embedding_model=settings.GEMINI_EMBEDDING_MODEL,
    )
