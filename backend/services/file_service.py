import shutil
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException

from backend.config import settings


class FileService:
    """
    Handles file validation and persistence.

    v0.2.0 change: files are no longer deleted after analysis.
    They are stored as uploads/<uuid>.<ext> and served for playback.
    The analysis_id IS the uuid, so the audio URL is deterministic.
    """

    def __init__(self) -> None:
        settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    def validate(self, file: UploadFile) -> None:
        suffix = Path(file.filename or "").suffix.lower()
        if suffix not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=422,
                detail={
                    "detail": f"Unsupported format '{suffix}'. Use MP3, WAV, FLAC, OGG or M4A.",
                    "code": "INVALID_FORMAT",
                },
            )
        if file.size and file.size > settings.max_file_size_bytes:
            raise HTTPException(
                status_code=413,
                detail={
                    "detail": f"File exceeds {settings.MAX_FILE_SIZE_MB} MB limit.",
                    "code": "FILE_TOO_LARGE",
                },
            )

    async def save(self, file: UploadFile) -> tuple[Path, str]:
        """
        Save the file and return (path, analysis_id).
        The analysis_id is a UUID that becomes both the DB key and the audio URL token.
        """
        suffix = Path(file.filename or "upload").suffix.lower()
        analysis_id = uuid.uuid4().hex
        dest = settings.UPLOAD_DIR / f"{analysis_id}{suffix}"

        with dest.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        if dest.stat().st_size > settings.max_file_size_bytes:
            dest.unlink(missing_ok=True)
            raise HTTPException(
                status_code=413,
                detail={
                    "detail": f"File exceeds {settings.MAX_FILE_SIZE_MB} MB limit.",
                    "code": "FILE_TOO_LARGE",
                },
            )

        return dest, analysis_id

    def cleanup(self, path: Path) -> None:
        """Explicit cleanup — only called on analysis failure in v0.2.0."""
        path.unlink(missing_ok=True)

    def audio_path_for_id(self, analysis_id: str) -> Path | None:
        """Find the stored audio file for a given analysis_id."""
        for ext in settings.ALLOWED_EXTENSIONS:
            candidate = settings.UPLOAD_DIR / f"{analysis_id}{ext}"
            if candidate.exists():
                return candidate
        return None


file_service = FileService()
