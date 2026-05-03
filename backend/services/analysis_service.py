from pathlib import Path

from backend.config import settings
from backend.schemas.analysis import (
    AnalysisResult,
    FileMetadata,
)
# Audio modules — will be implemented in Step 4 & 5
from backend.audio.bpm import detect_bpm
from backend.audio.key import detect_key
from backend.audio.waveform import extract_waveform
from backend.audio.spectrogram import compute_spectrogram
from backend.audio.chords import detect_chords


class AnalysisService:
    """
    Orchestrates the full audio analysis pipeline.

    Responsibilities:
      1. Load audio once (shared numpy array across all processors)
      2. Call each DSP module in order
      3. Assemble the AnalysisResult schema
      4. Never do DSP math itself — that lives in audio/
    """

    async def analyze(self, audio_path: Path, original_filename: str) -> AnalysisResult:
        import librosa
        import soundfile as sf

        # --- 1. Load audio ---------------------------------------------------
        # librosa.load resamples to settings.SAMPLE_RATE automatically.
        # mono=True collapses stereo; we track original channel count separately.
        y, sr = librosa.load(str(audio_path), sr=settings.SAMPLE_RATE, mono=True)

        # Get original file metadata before any processing
        info = sf.info(str(audio_path))
        file_stat = audio_path.stat()

        metadata = FileMetadata(
            filename=original_filename,
            format=audio_path.suffix.lstrip(".").lower(),
            duration_seconds=round(float(info.duration), 3),
            sample_rate=info.samplerate,
            channels=info.channels,
            file_size_bytes=file_stat.st_size,
        )

        # --- 2. Run DSP pipeline (all modules receive the same y, sr) --------
        bpm_result = detect_bpm(y, sr)
        key_result = detect_key(y, sr)
        waveform_data = extract_waveform(y, sr)
        spectrogram_data = compute_spectrogram(y, sr)
        chord_events = detect_chords(y, sr)

        # --- 3. Assemble and return ------------------------------------------
        return AnalysisResult(
            metadata=metadata,
            bpm=bpm_result,
            key=key_result,
            waveform=waveform_data,
            spectrogram=spectrogram_data,
            chords=chord_events,
        )


# Module-level singleton
analysis_service = AnalysisService()
