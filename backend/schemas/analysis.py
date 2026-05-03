from pydantic import BaseModel, Field
from typing import Optional


class FileMetadata(BaseModel):
    filename: str
    format: str
    duration_seconds: float
    sample_rate: int
    channels: int
    file_size_bytes: int


class BPMResult(BaseModel):
    bpm: float = Field(..., description="Estimated tempo in BPM")
    confidence: float = Field(..., ge=0.0, le=1.0)


class KeyResult(BaseModel):
    key: str
    mode: str
    label: str
    confidence: float = Field(..., ge=0.0, le=1.0)


class WaveformData(BaseModel):
    samples: list[float]
    duration_seconds: float


class SpectrogramData(BaseModel):
    values: list[list[float]]
    time_axis: list[float]
    frequency_axis: list[float]
    db_min: float
    db_max: float


class ChordEvent(BaseModel):
    start_seconds: float
    end_seconds: float
    chord: str
    confidence: float = Field(..., ge=0.0, le=1.0)


class AnalysisResult(BaseModel):
    # v0.2.0: analysis_id enables audio playback + DB retrieval
    analysis_id: str
    metadata: FileMetadata
    bpm: BPMResult
    key: KeyResult
    waveform: WaveformData
    spectrogram: SpectrogramData
    chords: list[ChordEvent]
    summary: Optional[str] = None

    def model_post_init(self, __context) -> None:
        if self.summary is None:
            self.summary = f"{self.bpm.bpm:.1f} BPM · {self.key.label}"


class AnalysisSummary(BaseModel):
    """Lightweight record for the history list."""
    id: str
    filename: str
    format: str
    created_at: str


class ErrorResponse(BaseModel):
    detail: str
    code: str
