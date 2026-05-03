from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from backend.services.file_service import file_service
from backend.services.analysis_service import analysis_service
from backend.schemas.analysis import AnalysisResult, ErrorResponse

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.post(
    "/upload",
    response_model=AnalysisResult,
    responses={
        413: {"model": ErrorResponse, "description": "File too large"},
        422: {"model": ErrorResponse, "description": "Invalid format"},
        500: {"model": ErrorResponse, "description": "Analysis failed"},
    },
    summary="Upload an audio file and receive full musical analysis",
)
async def upload_and_analyze(
    file: UploadFile = File(..., description="MP3 or WAV file, max 50 MB"),
):
    """
    Main endpoint — the entire user journey in one call:
      1. Validate the file (format + size)
      2. Persist to disk
      3. Run analysis pipeline
      4. Return structured AnalysisResult
      5. Clean up temp file
    """
    # Validate before saving to avoid wasting I/O on bad uploads
    file_service.validate(file)

    audio_path = None
    try:
        audio_path = await file_service.save(file)
        result = await analysis_service.analyze(audio_path, file.filename or "upload")
        return result

    except HTTPException:
        raise  # pass validation errors through unchanged

    except Exception as exc:
        # Unexpected DSP or I/O error — log and return a clean 500
        # In production you'd log exc to your observability stack here
        raise HTTPException(
            status_code=500,
            detail={"detail": f"Analysis failed: {str(exc)}", "code": "ANALYSIS_ERROR"},
        ) from exc

    finally:
        # Always clean up the temp file, success or failure
        if audio_path:
            file_service.cleanup(audio_path)
