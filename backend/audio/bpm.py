import numpy as np
import librosa
from backend.schemas.analysis import BPMResult


def detect_bpm(y: np.ndarray, sr: int) -> BPMResult:
    """
    Estimate tempo and extract beat grid positions.

    Returns:
      - bpm            : global tempo in BPM
      - confidence     : autocorrelation-based confidence [0, 1]
      - beat_times     : timestamp (seconds) of every detected beat
      - downbeat_times : every 4th beat (bar start) — stronger visual marker

    The beat_times list is the key addition for the waveform overlay.
    librosa's beat tracker already computes these — we were just discarding them.
    """
    hop_length = 512

    y_perc    = librosa.effects.percussive(y, margin=3.0)
    onset_env = librosa.onset.onset_strength(y=y_perc, sr=sr, aggregate=np.median)

    tempo, beat_frames = librosa.beat.beat_track(
        onset_envelope=onset_env,
        sr=sr,
        hop_length=hop_length,
        trim=False,
        tightness=100,
    )

    bpm = float(np.atleast_1d(tempo)[0])

    # ── Confidence ────────────────────────────────────────────────────────
    ac = librosa.autocorrelate(onset_env, max_size=onset_env.size // 2)
    ac = librosa.util.normalize(ac, norm=np.inf)
    frames_per_sec     = sr / hop_length
    beat_period_frames = int(round(frames_per_sec * 60.0 / bpm))
    lo   = max(0, beat_period_frames - 5)
    hi   = min(len(ac) - 1, beat_period_frames + 5)
    peak = float(np.max(ac[lo:hi])) if lo < hi else 0.5
    confidence = float(np.clip((peak - 0.2) / 0.6, 0.0, 1.0))

    # ── Beat times ────────────────────────────────────────────────────────
    beat_times_arr = librosa.frames_to_time(beat_frames, sr=sr, hop_length=hop_length)
    beat_times     = [round(float(t), 4) for t in beat_times_arr]

    # ── Downbeats — every 4th beat starting from beat 0 ──────────────────
    # This is a heuristic: true downbeat detection needs a dedicated model.
    # For a visual overlay, every 4th beat is close enough for 4/4 time.
    downbeat_times = [beat_times[i] for i in range(0, len(beat_times), 4)]

    print(f"[BPM] detected={bpm:.1f}  beats={len(beat_times)}  "
          f"downbeats={len(downbeat_times)}  confidence={confidence:.2f}")

    return BPMResult(
        bpm=round(bpm, 1),
        confidence=round(confidence, 3),
        beat_times=beat_times,
        downbeat_times=downbeat_times,
    )
