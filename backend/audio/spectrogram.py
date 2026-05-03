import numpy as np
import librosa
from backend.schemas.analysis import SpectrogramData
from backend.config import settings


def compute_spectrogram(y: np.ndarray, sr: int) -> SpectrogramData:
    """
    Compute a mel spectrogram (dB-scaled) suitable for heatmap rendering.

    Output shape: [time_frames][mel_bins]
    Values are dB relative to the peak, floored at -80 dB.

    We limit time resolution to ~200 frames for response size — the frontend
    renders this as a pixelated heatmap so sub-frame precision isn't needed.
    """
    n_mels    = settings.SPECTROGRAM_BINS   # frequency resolution (mel bands)
    hop_length = 512
    max_frames = 200   # cap time axis for payload size

    # Compute mel spectrogram
    S = librosa.feature.melspectrogram(
        y=y,
        sr=sr,
        n_mels=n_mels,
        hop_length=hop_length,
        fmax=sr // 2,
    )

    # Convert to dB scale
    S_db = librosa.power_to_db(S, ref=np.max)  # values in [-80, 0] dB

    # Downsample time axis if too many frames
    n_frames = S_db.shape[1]
    if n_frames > max_frames:
        # Average-pool along time axis
        indices = np.linspace(0, n_frames - 1, max_frames, dtype=int)
        S_db    = S_db[:, indices]

    # Build time axis (seconds)
    n_out_frames = S_db.shape[1]
    duration     = len(y) / sr
    time_axis    = [round(float(t), 3)
                    for t in np.linspace(0, duration, n_out_frames)]

    # Build frequency axis (mel band centre frequencies in Hz)
    mel_freqs = librosa.mel_frequencies(n_mels=n_mels, fmax=sr // 2)
    freq_axis = [round(float(f), 1) for f in mel_freqs]

    # Transpose to [time][freq] for JSON serialisation
    values = [
        [round(float(v), 2) for v in S_db[:, t]]
        for t in range(n_out_frames)
    ]

    db_min = float(np.min(S_db))
    db_max = float(np.max(S_db))

    print(f"[SPECTROGRAM] frames={n_out_frames}  mels={n_mels}  "
          f"db=[{db_min:.1f}, {db_max:.1f}]")

    return SpectrogramData(
        values=values,
        time_axis=time_axis,
        frequency_axis=freq_axis,
        db_min=round(db_min, 2),
        db_max=round(db_max, 2),
    )
