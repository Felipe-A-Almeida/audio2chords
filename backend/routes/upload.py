# backend/routes/upload.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Annotated
from backend.services.file_service import file_service
from backend.services.analysis_service import analysis_service
from backend.schemas.analysis import AnalysisResult, ErrorResponse
from backend.audio.stems import StemMode
from backend.db import save_analysis

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

@router.post("/upload", response_model=AnalysisResult,
    responses={413:{"model":ErrorResponse},422:{"model":ErrorResponse},500:{"model":ErrorResponse}})
async def upload_and_analyze(
    file: UploadFile = File(...),
    stem_mode: Annotated[StemMode, Form()] = StemMode.HARMONIC,
):
    file_service.validate(file)
    audio_path = analysis_id = None
    try:
        audio_path, analysis_id = await file_service.save(file)
        result = await analysis_service.analyze(
            audio_path, file.filename or "upload", analysis_id, stem_mode=stem_mode)
        await save_analysis(analysis_id=analysis_id, filename=file.filename or "upload",
                            fmt=audio_path.suffix.lstrip(".").lower(), result_dict=result.model_dump())
        return result
    except HTTPException:
        raise
    except Exception as exc:
        if audio_path: file_service.cleanup(audio_path)
        raise HTTPException(status_code=500,
            detail={"detail":f"Analysis failed: {str(exc)}","code":"ANALYSIS_ERROR"}) from exc
