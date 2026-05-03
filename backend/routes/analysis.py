from fastapi import APIRouter
from fastapi.responses import JSONResponse
from backend.schemas.analysis import AnalysisResult

router = APIRouter(prefix="/api", tags=["utility"])


@router.get("/health", summary="Health check")
async def health():
    """Simple liveness probe."""
    return {"status": "ok", "service": "AudioChord"}


@router.post(
    "/export",
    summary="Re-export an existing analysis result as a downloadable JSON file",
)
async def export_analysis(result: AnalysisResult):
    """
    Receives a full AnalysisResult payload and returns it as a
    Content-Disposition: attachment response so the browser triggers a download.
    
    The frontend calls this after displaying results — the user clicks
    'Export JSON' and the browser saves the file.
    """
    filename = f"audiochord_{result.metadata.filename}.json"
    return JSONResponse(
        content=result.model_dump(),
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
