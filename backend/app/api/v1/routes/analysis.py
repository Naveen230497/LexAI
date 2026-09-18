"""Full analysis route handler — simplification + risk analysis in parallel."""

import asyncio
from fastapi import APIRouter, HTTPException, Request

from app.schemas.analysis import FullAnalysisResult, SimplificationResult, RiskAnalysisResult
from app.core.gemini_client import get_gemini_client
from app.core.document_processor import chunk_document
from app.core.rag_engine import RAGEngine
from app.core.cache import response_cache
from app.config import get_settings
from app.limiter import limiter
from app.prompts.simplification import build_simplification_prompt
from app.prompts.risk_analysis import build_risk_analysis_prompt

router = APIRouter(tags=["Analysis"])


@router.post("/{session_id}/full", response_model=FullAnalysisResult)
async def run_full_analysis(
    session_id: str,
    request: Request,
) -> FullAnalysisResult:
    from app.api.v1.routes.documents import SESSION_STORE
    
    if session_id not in SESSION_STORE:
        raise HTTPException(status_code=404, detail="Session not found.")
        
    doc_info = SESSION_STORE[session_id]
    text_content = doc_info["text"]
    
    cache_key = response_cache.make_key(text_content.encode('utf-8'), "full_analysis")
    cached_result = response_cache.get(cache_key)
    if cached_result:
        return FullAnalysisResult(**cached_result)

    gemini_client = get_gemini_client()
    settings = get_settings()

    try:
        # Run sequentially to avoid bursting the 5 RPM free tier limit
        simp_prompt = build_simplification_prompt(text_content)
        simplification_raw = await gemini_client.generate_json(simp_prompt)
        
        risk_prompt = build_risk_analysis_prompt(text_content)
        risk_raw = await gemini_client.generate_json(risk_prompt)
        
        # Prepare vector DB in background while waiting
        rag = RAGEngine(
            session_id=session_id,
            chroma_dir=settings.CHROMA_DIR,
            gemini_client=gemini_client,
            embedding_model=settings.GEMINI_EMBEDDING_MODEL,
        )
        chunks = chunk_document(text_content)
        rag.index_document(chunks)
        
    except Exception as exc:
        with open("error_log.txt", "a") as f:
            import traceback
            f.write("--- Analysis Error ---\n")
            f.write(traceback.format_exc())
            f.write("\n")
        
        err_msg = str(exc).lower()
        if "quota" in err_msg or "exhausted" in err_msg or "429" in err_msg:
            raise HTTPException(
                status_code=429, 
                detail="Google Gemini API Rate Limit Exceeded. Please wait 60 seconds and try again."
            )
        raise HTTPException(status_code=500, detail=f"Gemini API Error: {exc}")

    try:
        simp_result = SimplificationResult(**simplification_raw)
        risk_result = RiskAnalysisResult(**risk_raw)
    except Exception as exc:
        with open("error_log.txt", "a") as f:
            import traceback
            f.write("--- Parsing Error ---\n")
            f.write(traceback.format_exc())
            f.write(f"\nRaw Simplification: {simplification_raw}\nRaw Risk: {risk_raw}\n")
        raise HTTPException(
            status_code=500,
            detail="Failed to parse analysis results from LLM.",
        ) from exc

    final_result = FullAnalysisResult(
        simplification=simp_result,
        risk_analysis=risk_result,
    )
    
    response_cache.set(cache_key, final_result.model_dump())
    return final_result
