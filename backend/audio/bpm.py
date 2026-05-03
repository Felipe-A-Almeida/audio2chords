import numpy as np
import librosa
from backend.schemas.analysis import BPMResult


def detect_bpm(y: np.ndarray, sr: int) -> BPMResult:
    """
    Estimate tempo using librosa's beat tracker.

    Strategy:
      1. Compute onset strength envelope (percussive events over time)
      2. Run dynamic programming beat tracker → gives global tempo + beat frames
      3. Derive confidence from the autocorrelation peak ratio of the onset envelope
         at the detected period — higher peak = more rhythmically consistent signal.

    Returns BPMResult with bpm rounded to 1 decimal and confidence in [0, 1].
    """
    # Separate percussive component — helps with melodic/harmonic-heavy tracks
    # where the beat tracker can get confused by sustained notes
    y_perc = librosa.effects.percussive(y, margin=3.0)

    # Onset strength envelope
    onset_env = librosa.onset.onset_strength(y=y_perc, sr=sr, aggregate=np.median)

    # Beat tracking — returns global tempo and beat frame indices
    tempo, beat_frames = librosa.beat.beat_track(
        onset_envelope=onset_env,
        sr=sr,
        trim=False,         # don't trim leading/trailing silence before tracking
        tightness=100,      # how strictly beats follow the tempo grid (default 100)
    )

    # Scalar tempo (librosa may return array in some versions)
    bpm = float(np.atleast_1d(tempo)[0])

    # --- Confidence estimation -------------------------------------------
    # Use the normalized autocorrelation of the onset envelope.
    # At the lag corresponding to one beat period, a strong peak means
    # the signal is highly periodic → high confidence.
    ac = librosa.autocorrelate(onset_env, max_size=onset_env.size // 2)
    ac = librosa.util.normalize(ac, norm=np.inf)

    # Convert BPM → lag in onset frames
    hop_length  = 512                          # librosa default
    frames_per_sec = sr / hop_length
    beat_period_frames = int(round(frames_per_sec * 60.0 / bpm))

    # Search ±5 frames around expected period to find actual peak
    lo = max(0, beat_period_frames - 5)
    hi = min(len(ac) - 1, beat_period_frames + 5)
    peak = float(np.max(ac[lo:hi])) if lo < hi else 0.5

    # Clamp and scale: peaks above 0.5 are fairly confident
    confidence = float(np.clip((peak - 0.2) / 0.6, 0.0, 1.0))

    print(f"[BPM] detected={bpm:.1f}  beats={len(beat_frames)}  confidence={confidence:.2f}")

    return BPMResult(bpm=round(bpm, 1), confidence=round(confidence, 3))
