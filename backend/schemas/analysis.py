from pydantic import BaseModel, Field
from typing import Optional


class FileMetadata(BaseModel):
    """Basic info about the uploaded file."""
    filename: str
    format: str           # "mp3" or "wav"
    duration_seconds: float
    sample_rate: int
    channels: int
    file_size_bytes: int


class BPMResult(BaseModel):
    bpm: float = Field(..., description="Estimated tempo in beats per minute")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence 0–1")


class KeyResult(BaseModel):
    key: str              # e.g. "A", "C#"
    mode: str             # "major" or "minor"
    label: str            # e.g. "A minor"
    confidence: float = Field(..., ge=0.0, le=1.0)


class WaveformData(BaseModel):
    """Downsampled amplitude data for rendering."""
    samples: list[float]  # normalised amplitude values in [-1, 1]
    duration_seconds: float


class SpectrogramData(BaseModel):
    """
    Mel spectrogram as a 2-D list (time × frequency).
    Values are dB-scaled. Frontend renders as a heatmap.
    """
    values: list[list[float]]   # shape: [time_frames][mel_bins]
    time_axis: list[float]      # seconds for each time frame
    frequency_axis: list[float] # Hz for each mel bin (centre freqs)
    db_min: float
    db_max: float


class ChordEvent(BaseModel):
    """A single chord detected in the timeline."""
    start_seconds: float
    end_seconds: float
    chord: str            # e.g. "Am", "F", "C", "G7"
    confidence: float = Field(..., ge=0.0, le=1.0)


class AnalysisResult(BaseModel):
    """
    Top-level response returned by POST /api/analysis/upload.
    This is also the shape exported as JSON.
    """
    metadata: FileMetadata
    bpm: BPMResult
    key: KeyResult
    waveform: WaveformData
    spectrogram: SpectrogramData
    chords: list[ChordEvent]

    # Convenience: full label for display (e.g. "120 BPM · A minor")
    summary: Optional[str] = None

    def model_post_init(self, __context) -> None:
        if self.summary is None:
            self.summary = (
                f"{self.bpm.bpm:.1f} BPM · {self.key.label}"
            )


class ErrorResponse(BaseModel):
    detail: str
    code: str             # machine-readable error code for the frontend
