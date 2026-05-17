from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, FileResponse

from backend.schemas.analysis import AnalysisResult, AnalysisSummary, ErrorResponse
from backend.db import load_analysis, list_analyses
from backend.services.file_service import file_service
from backend.config import settings

router = APIRouter(prefix="/api", tags=["utility"])


@router.get("/health", summary="Health check")
async def health():
    return {"status": "ok", "service": "AudioChord", "version": "0.4.2"}


# ── Audio serving ─────────────────────────────────────────────────────────

MIME_MAP = {
    ".mp3": "audio/mpeg", ".wav": "audio/wav",
    ".flac": "audio/flac", ".ogg": "audio/ogg", ".m4a": "audio/mp4",
}

@router.get(
    "/audio/{analysis_id}",
    summary="Stream original audio for playback",
    responses={404: {"model": ErrorResponse}},
)
async def serve_audio(analysis_id: str):
    path = file_service.audio_path_for_id(analysis_id)
    if not path:
        raise HTTPException(status_code=404, detail={
            "detail": "Audio file not found.", "code": "AUDIO_NOT_FOUND"
        })
    media_type = MIME_MAP.get(path.suffix.lower(), "application/octet-stream")
    return FileResponse(str(path), media_type=media_type,
                        headers={"Accept-Ranges": "bytes"})


@router.get(
    "/audio/{analysis_id}/harmonic",
    summary="Stream harmonic stem (no drums/bass) for playback",
    responses={404: {"model": ErrorResponse}},
)
async def serve_harmonic(analysis_id: str):
    """
    Returns the harmonic stem WAV saved during analysis.
    Only available when Demucs or HPSS produced a stem file.
    The frontend uses this for the Original / Harmonic playback toggle.
    """
    path = settings.UPLOAD_DIR / f"{analysis_id}.harmonic.wav"
    if not path.exists():
        raise HTTPException(status_code=404, detail={
            "detail": "Harmonic stem not available for this analysis.",
            "code": "HARMONIC_NOT_FOUND",
        })
    return FileResponse(str(path), media_type="audio/wav",
                        headers={"Accept-Ranges": "bytes"})


# ── History ───────────────────────────────────────────────────────────────

@router.get("/history", response_model=list[AnalysisSummary],
            summary="List recent analyses")
async def get_history():
    return await list_analyses(limit=20)


@router.get("/analysis/{analysis_id}", response_model=AnalysisResult,
            summary="Retrieve a saved analysis result",
            responses={404: {"model": ErrorResponse}})
async def get_analysis(analysis_id: str):
    data = await load_analysis(analysis_id)
    if not data:
        raise HTTPException(status_code=404, detail={
            "detail": "Analysis not found.", "code": "NOT_FOUND"
        })
    return data


# ── JSON export ───────────────────────────────────────────────────────────

@router.post("/export", summary="Download analysis as JSON file")
async def export_analysis(result: AnalysisResult):
    filename = f"audiochord_{result.metadata.filename}.json"
    return JSONResponse(
        content=result.model_dump(),
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
