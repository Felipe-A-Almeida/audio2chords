from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.services.file_service import file_service
from backend.services.analysis_service import analysis_service
from backend.schemas.analysis import AnalysisResult, ErrorResponse
from backend.db import save_analysis

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.post(
    "/upload",
    response_model=AnalysisResult,
    responses={
        413: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    summary="Upload an audio file and receive full musical analysis",
)
async def upload_and_analyze(
    file: UploadFile = File(..., description="MP3, WAV, FLAC, OGG or M4A — max 50 MB"),
):
    """
    v0.2.0 changes:
    - file_service.save() returns (path, analysis_id)
    - audio file is kept on disk for playback
    - result is persisted to SQLite
    - cleanup only on failure
    """
    file_service.validate(file)

    audio_path   = None
    analysis_id  = None
    try:
        audio_path, analysis_id = await file_service.save(file)
        result = await analysis_service.analyze(audio_path, file.filename or "upload", analysis_id)

        # Persist to SQLite for history + re-retrieval
        await save_analysis(
            analysis_id=analysis_id,
            filename=file.filename or "upload",
            fmt=audio_path.suffix.lstrip(".").lower(),
            result_dict=result.model_dump(),
        )

        return result

    except HTTPException:
        raise

    except Exception as exc:
        # Only clean up on failure — on success we keep the file for playback
        if audio_path:
            file_service.cleanup(audio_path)
        raise HTTPException(
            status_code=500,
            detail={"detail": f"Analysis failed: {str(exc)}", "code": "ANALYSIS_ERROR"},
        ) from exc
