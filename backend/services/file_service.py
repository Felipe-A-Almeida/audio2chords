import shutil
from pathlib import Path
from fastapi import UploadFile, HTTPException

from backend.config import settings
from backend.utils.helpers import generate_upload_path


class FileService:
    """
    Handles file validation and persistence.
    Keeps all I/O concerns out of the route layer.
    """

    def __init__(self) -> None:
        # Ensure upload directory exists at startup
        settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    def validate(self, file: UploadFile) -> None:
        """
        Raise HTTP 422 if the file fails any validation rule.
        Called before touching the filesystem.
        """
        suffix = Path(file.filename or "").suffix.lower()

        if suffix not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=422,
                detail={
                    "detail": f"Unsupported format '{suffix}'. Use MP3 or WAV.",
                    "code": "INVALID_FORMAT",
                },
            )

        # content_length may be None for chunked uploads — we re-check after save
        if file.size and file.size > settings.max_file_size_bytes:
            raise HTTPException(
                status_code=413,
                detail={
                    "detail": f"File exceeds {settings.MAX_FILE_SIZE_MB} MB limit.",
                    "code": "FILE_TOO_LARGE",
                },
            )

    async def save(self, file: UploadFile) -> Path:
        """
        Persist the uploaded file and return its path.
        Validates size again after saving (handles chunked uploads).
        """
        dest = generate_upload_path(file.filename or "upload")

        with dest.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Post-save size check (covers chunked transfers)
        if dest.stat().st_size > settings.max_file_size_bytes:
            dest.unlink(missing_ok=True)
            raise HTTPException(
                status_code=413,
                detail={
                    "detail": f"File exceeds {settings.MAX_FILE_SIZE_MB} MB limit.",
                    "code": "FILE_TOO_LARGE",
                },
            )

        return dest

    def cleanup(self, path: Path) -> None:
        """Delete a file after analysis is complete (optional — call explicitly)."""
        path.unlink(missing_ok=True)


# Module-level singleton
file_service = FileService()
