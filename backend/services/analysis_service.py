from pathlib import Path
from backend.config import settings
from backend.schemas.analysis import AnalysisResult, FileMetadata, StemInfo
from backend.audio.bpm import detect_bpm
from backend.audio.key import detect_key
from backend.audio.waveform import extract_waveform
from backend.audio.spectrogram import compute_spectrogram
from backend.audio.chords import detect_chords
from backend.audio.stems import separate, save_harmonic_stem, StemMode


class AnalysisService:

    async def analyze(
        self,
        audio_path: Path,
        original_filename: str,
        analysis_id: str,
        stem_mode: StemMode = StemMode.HARMONIC,   # ← new parameter
    ) -> AnalysisResult:
        import librosa
        import soundfile as sf

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

        # Stem separation — runs once, shared across all DSP modules
        stems = separate(y, sr, audio_path, mode=stem_mode)
        print(f"[ANALYSIS] Stem: method={stems.method} mode={stems.mode} quality={stems.quality}")

        # Save harmonic stem for playback toggle
        harmonic_available = False
        harmonic_path = audio_path.parent / f"{analysis_id}.harmonic.wav"
        try:
            save_harmonic_stem(stems, sr, harmonic_path)
            harmonic_available = True
        except Exception as e:
            print(f"[ANALYSIS] Could not save harmonic stem: {e}")

        stem_info = StemInfo(
            method=stems.method,
            model=stems.model,
            quality=stems.quality,
            mode=stems.mode,
            demucs_available=stems.method == "demucs",
            vocal_removal=stems.mode == "instrumental" and stems.method == "demucs",
            harmonic_available=harmonic_available,
        )

        bpm_result       = detect_bpm(y, sr, stems=stems)
        key_result       = detect_key(y, sr, stems=stems)
        waveform_data    = extract_waveform(y, sr)
        spectrogram_data = compute_spectrogram(y, sr)
        chord_events     = detect_chords(y, sr, stems=stems)

        return AnalysisResult(
            analysis_id=analysis_id,
            metadata=metadata,
            stem_info=stem_info,
            bpm=bpm_result,
            key=key_result,
            waveform=waveform_data,
            spectrogram=spectrogram_data,
            chords=chord_events,
        )


analysis_service = AnalysisService()