from pathlib import Path

from backend.config import settings
from backend.schemas.analysis import AnalysisResult, FileMetadata
from backend.audio.bpm import detect_bpm
from backend.audio.key import detect_key
from backend.audio.waveform import extract_waveform
from backend.audio.spectrogram import compute_spectrogram
from backend.audio.chords import detect_chords


class AnalysisService:
    """
    Orchestrates the full audio analysis pipeline.

    v0.2.0: receives analysis_id from file_service (no longer generates it here),
    passes it through to AnalysisResult so the frontend can build the audio URL.
    """

    async def analyze(
        self,
        audio_path: Path,
        original_filename: str,
        analysis_id: str,
    ) -> AnalysisResult:
        import librosa
        import soundfile as sf

        # Load audio — resample to SAMPLE_RATE, collapse to mono
        y, sr = librosa.load(str(audio_path), sr=settings.SAMPLE_RATE, mono=True)

        info      = sf.info(str(audio_path))
        file_stat = audio_path.stat()

        metadata = FileMetadata(
            filename=original_filename,
            format=audio_path.suffix.lstrip(".").lower(),
            duration_seconds=round(float(info.duration), 3),
            sample_rate=info.samplerate,
            channels=info.channels,
            file_size_bytes=file_stat.st_size,
        )

        # DSP pipeline — all modules share the same y, sr
        bpm_result       = detect_bpm(y, sr)
        key_result       = detect_key(y, sr)
        waveform_data    = extract_waveform(y, sr)
        spectrogram_data = compute_spectrogram(y, sr)
        chord_events     = detect_chords(y, sr)

        return AnalysisResult(
            analysis_id=analysis_id,
            metadata=metadata,
            bpm=bpm_result,
            key=key_result,
            waveform=waveform_data,
            spectrogram=spectrogram_data,
            chords=chord_events,
        )


analysis_service = AnalysisService()
