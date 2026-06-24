from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # App
    APP_NAME: str = "AudioChord"
    APP_VERSION: str = "0.2.0"
    DEBUG: bool = True

    # CORS — Vue dev server runs on 5173
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # File upload
    UPLOAD_DIR: Path = Path("uploads")
    MAX_FILE_SIZE_MB: int = 50
    # v0.2.0: added flac, ogg, m4a support via ffmpeg
    ALLOWED_EXTENSIONS: set[str] = {".mp3", ".wav", ".flac", ".ogg", ".m4a"}

    # Audio analysis
    SAMPLE_RATE: int = 22050
    WAVEFORM_POINTS: int = 2000
    SPECTROGRAM_BINS: int = 128
    CHORD_HOP_SECONDS: float = 0.5

    # v0.2.0: keep audio files for playback (they are cleaned up by DB TTL in future)
    KEEP_AUDIO_FILES: bool = True

    # Rate limiting (per IP)
    RATE_LIMIT_UPLOAD_MINUTE: int = 5
    RATE_LIMIT_UPLOAD_HOUR: int = 20

    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
