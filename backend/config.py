from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # App
    APP_NAME: str = "AudioChord"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # CORS — Vue dev server runs on 5173
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # File upload
    UPLOAD_DIR: Path = Path("uploads")
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: set[str] = {".mp3", ".wav"}

    # Audio analysis
    SAMPLE_RATE: int = 22050        # librosa default; good balance of quality vs speed
    WAVEFORM_POINTS: int = 2000     # number of amplitude samples sent to frontend
    SPECTROGRAM_BINS: int = 128     # mel bands for spectrogram
    CHORD_HOP_SECONDS: float = 0.5  # how often to sample chord changes

    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


# Single shared instance — import this everywhere
settings = Settings()
