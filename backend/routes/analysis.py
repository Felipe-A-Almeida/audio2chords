from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, FileResponse

from backend.schemas.analysis import AnalysisResult, AnalysisSummary, ErrorResponse
from backend.db import load_analysis, list_analyses
from backend.services.file_service import file_service

router = APIRouter(prefix="/api", tags=["utility"])


@router.get("/health", summary="Health check")
async def health():
    return {"status": "ok", "service": "AudioChord", "version": "0.2.0"}


# ---------------------------------------------------------------------------
# Audio file serving — enables browser playback
# ---------------------------------------------------------------------------
@router.get(
    "/audio/{analysis_id}",
    summary="Stream the original audio file for in-browser playback",
    responses={404: {"model": ErrorResponse}},
)
async def serve_audio(analysis_id: str):
    """
    Returns the stored audio file so the frontend can play it via
    HTMLAudioElement. The analysis_id in the URL matches the UUID
    assigned during upload — no lookup needed, path is deterministic.
    """
    path = file_service.audio_path_for_id(analysis_id)
    if not path:
        raise HTTPException(
            status_code=404,
            detail={"detail": "Audio file not found.", "code": "AUDIO_NOT_FOUND"},
        )

    # Map extension to MIME type
    mime_map = {
        ".mp3":  "audio/mpeg",
        ".wav":  "audio/wav",
        ".flac": "audio/flac",
        ".ogg":  "audio/ogg",
        ".m4a":  "audio/mp4",
    }
    media_type = mime_map.get(path.suffix.lower(), "application/octet-stream")

    return FileResponse(
        path=str(path),
        media_type=media_type,
        headers={"Accept-Ranges": "bytes"},  # enables browser seeking
    )


# ---------------------------------------------------------------------------
# History — list recent analyses from SQLite
# ---------------------------------------------------------------------------
@router.get(
    "/history",
    response_model=list[AnalysisSummary],
    summary="List recent analyses",
)
async def get_history():
    return await list_analyses(limit=20)


# ---------------------------------------------------------------------------
# Retrieve a saved analysis by ID
# ---------------------------------------------------------------------------
@router.get(
    "/analysis/{analysis_id}",
    response_model=AnalysisResult,
    summary="Retrieve a saved analysis result",
    responses={404: {"model": ErrorResponse}},
)
async def get_analysis(analysis_id: str):
    data = await load_analysis(analysis_id)
    if not data:
        raise HTTPException(
            status_code=404,
            detail={"detail": "Analysis not found.", "code": "NOT_FOUND"},
        )
    return data


# ---------------------------------------------------------------------------
# JSON export
# ---------------------------------------------------------------------------
@router.post("/export", summary="Download analysis as JSON file")
async def export_analysis(result: AnalysisResult):
    filename = f"audiochord_{result.metadata.filename}.json"
    return JSONResponse(
        content=result.model_dump(),
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
