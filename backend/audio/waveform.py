import numpy as np
import librosa
from backend.schemas.analysis import WaveformData
from backend.config import settings


def extract_waveform(y: np.ndarray, sr: int) -> WaveformData:
    """
    Downsample the raw waveform to WAVEFORM_POINTS samples for frontend rendering.

    Strategy: frame-based RMS downsampling rather than naive slicing.
    Each output point = RMS amplitude of a frame, preserving the visual
    envelope shape even when compressing by 100x or more.
    Signed: we alternate the sign based on whether the frame's mean is
    positive or negative, giving the frontend a realistic waveform shape.
    """
    duration = len(y) / sr
    n_points = settings.WAVEFORM_POINTS

    # Frame size: how many input samples map to one output point
    frame_size = max(1, len(y) // n_points)

    samples = []
    for i in range(n_points):
        start = i * frame_size
        end   = min(start + frame_size, len(y))
        if start >= len(y):
            samples.append(0.0)
            continue
        frame = y[start:end]
        rms   = float(np.sqrt(np.mean(frame ** 2)))
        sign  = 1.0 if float(np.mean(frame)) >= 0 else -1.0
        samples.append(round(sign * rms, 5))

    # Normalise to [-1, 1] so all tracks render at the same visual scale
    peak = max(abs(s) for s in samples) or 1.0
    samples = [round(s / peak, 5) for s in samples]

    print(f"[WAVEFORM] points={len(samples)}  peak={peak:.4f}  duration={duration:.2f}s")

    return WaveformData(
        samples=samples,
        duration_seconds=round(duration, 3),
    )
