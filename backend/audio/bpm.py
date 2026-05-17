import numpy as np
import librosa
from backend.schemas.analysis import BPMResult
from backend.audio.stems import StemResult


def detect_bpm(y: np.ndarray, sr: int, stems: StemResult | None = None) -> BPMResult:
    """
    Estimate tempo and extract beat grid positions.

    v0.4.2: accepts StemResult to use the clean percussive stem for beat tracking.
    When Demucs is available, the drums stem gives a much cleaner onset envelope
    than the raw mix — especially on music with heavy reverb or dense arrangements.

    Falls back to librosa percussive separation on the raw signal when no stems.
    """
    hop_length = 512

    # Use Demucs drums stem if available, otherwise separate percussive from raw
    if stems is not None and stems.method == "demucs" and stems.percussive is not None:
        y_perc = stems.percussive
        log.info("[BPM] Using Demucs drums stem for beat tracking")
    else:
        y_perc = librosa.effects.percussive(y, margin=3.0)

    onset_env = librosa.onset.onset_strength(y=y_perc, sr=sr, aggregate=np.median)

    tempo, beat_frames = librosa.beat.beat_track(
        onset_envelope=onset_env,
        sr=sr,
        hop_length=hop_length,
        trim=False,
        tightness=100,
    )

    bpm = float(np.atleast_1d(tempo)[0])

    # Confidence via autocorrelation peak at beat period
    ac = librosa.autocorrelate(onset_env, max_size=onset_env.size // 2)
    ac = librosa.util.normalize(ac, norm=np.inf)
    frames_per_sec     = sr / hop_length
    beat_period_frames = int(round(frames_per_sec * 60.0 / bpm))
    lo   = max(0, beat_period_frames - 5)
    hi   = min(len(ac) - 1, beat_period_frames + 5)
    peak = float(np.max(ac[lo:hi])) if lo < hi else 0.5
    confidence = float(np.clip((peak - 0.2) / 0.6, 0.0, 1.0))

    # Beat times and downbeats
    beat_times_arr = librosa.frames_to_time(beat_frames, sr=sr, hop_length=hop_length)
    beat_times     = [round(float(t), 4) for t in beat_times_arr]
    downbeat_times = [beat_times[i] for i in range(0, len(beat_times), 4)]

    print(f"[BPM] detected={bpm:.1f}  beats={len(beat_times)}  "
          f"downbeats={len(downbeat_times)}  confidence={confidence:.2f}")

    return BPMResult(
        bpm=round(bpm, 1),
        confidence=round(confidence, 3),
        beat_times=beat_times,
        downbeat_times=downbeat_times,
    )


import logging
log = logging.getLogger(__name__)
