from pathlib import Path
from backend.config import settings
from backend.schemas.analysis import AnalysisResult, FileMetadata
from backend.audio.bpm import detect_bpm
from backend.audio.key import detect_key
from backend.audio.waveform import extract_waveform
from backend.audio.spectrogram import compute_spectrogram
from backend.audio.chords import detect_chords
from backend.audio.stems import stem_info


class AnalysisService:
    async def analyze(self, audio_path: Path, original_filename: str,
                      analysis_id: str) -> AnalysisResult:
        import librosa, soundfile as sf

        info = stem_info()
        print(f"[ANALYSIS] Stem method: {info['method']} ({info['quality']} quality)")

        y, sr = librosa.load(str(audio_path), sr=settings.SAMPLE_RATE, mono=True)

        sf_info   = sf.info(str(audio_path))
        file_stat = audio_path.stat()

        metadata = FileMetadata(
            filename=original_filename,
            format=audio_path.suffix.lstrip(".").lower(),
            duration_seconds=round(float(sf_info.duration), 3),
            sample_rate=sf_info.samplerate,
            channels=sf_info.channels,
            file_size_bytes=file_stat.st_size,
        )

        bpm_result       = detect_bpm(y, sr)
        # Pass audio_path so Demucs can load at native SR if available
        key_result       = detect_key(y, sr, audio_path)
        waveform_data    = extract_waveform(y, sr)
        spectrogram_data = compute_spectrogram(y, sr)
        chord_events     = detect_chords(y, sr, audio_path)

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
