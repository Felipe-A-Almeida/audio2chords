import uuid
from pathlib import Path
from backend.config import settings


def generate_upload_path(original_filename: str) -> Path:
    """
    Build a unique path inside UPLOAD_DIR to avoid name collisions.
    Returns: uploads/<uuid><suffix>  e.g. uploads/3f2a…b1.mp3
    """
    suffix = Path(original_filename).suffix.lower()
    unique_name = f"{uuid.uuid4().hex}{suffix}"
    return settings.UPLOAD_DIR / unique_name


def format_duration(seconds: float) -> str:
    """Convert float seconds to 'mm:ss' string for display."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def clamp(value: float, lo: float, hi: float) -> float:
    """Clamp a value between lo and hi."""
    return max(lo, min(hi, value))
