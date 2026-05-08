"""
Stem separation — isolates harmonic/vocal content before DSP analysis.

Two strategies, selected automatically:

  1. Demucs (optional, high quality)
     Requires: pip install demucs
     Uses a pretrained neural network (htdemucs) to separate:
     vocals, bass, drums, other → we use vocals+other for chord/key analysis
     Produces significantly better results on polyphonic music.

  2. Librosa HPSS (always available, fast)
     Median-filter harmonic-percussive source separation.
     Good enough for most pop/rock, degrades on dense orchestral material.

The function returns a mono numpy array ready for further DSP.
Detection of demucs is done at call time — if it's installed it's used,
otherwise we fall back to HPSS with a log message.
"""

import numpy as np
import tempfile
import logging
from pathlib import Path

log = logging.getLogger(__name__)


def separate_harmonic(y: np.ndarray, sr: int, audio_path: Path | None = None) -> np.ndarray:
    """
    Return the harmonic/melodic component of the audio signal.

    Args:
        y          : mono audio array (already loaded by librosa)
        sr         : sample rate
        audio_path : original file path (required for Demucs, optional otherwise)

    Returns:
        y_harmonic : mono numpy array, same sr as input
    """
    if _demucs_available():
        try:
            return _separate_demucs(audio_path, sr)
        except Exception as e:
            log.warning(f"[STEMS] Demucs failed ({e}), falling back to HPSS")

    return _separate_hpss(y)


def _demucs_available() -> bool:
    try:
        import demucs  # noqa: F401
        return True
    except ImportError:
        return False


def _separate_hpss(y: np.ndarray) -> np.ndarray:
    """
    Librosa harmonic-percussive source separation.
    margin=6.0 is more aggressive than the default (margin=1) —
    it removes more percussive content at the cost of some harmonic bleed.
    """
    import librosa
    log.info("[STEMS] Using librosa HPSS (Demucs not installed)")
    y_harm, _ = librosa.effects.hpss(y, margin=6.0)
    return y_harm


def _separate_demucs(audio_path: Path, sr: int) -> np.ndarray:
    """
    Use Demucs htdemucs model to separate stems.
    We sum vocals + other → harmonic signal for chord/key analysis.
    Drums and bass are intentionally excluded to reduce chroma noise.

    Demucs outputs at 44100 Hz — we resample to match the project SR.
    """
    import torch
    import librosa
    from demucs.pretrained import get_model
    from demucs.apply import apply_model

    log.info("[STEMS] Using Demucs htdemucs for stem separation")

    model = get_model("htdemucs")
    model.eval()

    # Load at native rate for Demucs
    y_native, sr_native = librosa.load(str(audio_path), sr=None, mono=False)
    if y_native.ndim == 1:
        y_native = np.stack([y_native, y_native])  # stereo expected

    wav = torch.tensor(y_native, dtype=torch.float32).unsqueeze(0)  # (1, 2, T)

    with torch.no_grad():
        sources = apply_model(model, wav, device="cpu", progress=False)
    # sources shape: (1, 4, 2, T) — stems: drums, bass, other, vocals
    # Demucs stem order for htdemucs: drums=0, bass=1, other=2, vocals=3
    other  = sources[0, 2].mean(0).numpy()   # mono other
    vocals = sources[0, 3].mean(0).numpy()   # mono vocals

    harmonic = (other + vocals) / 2.0

    # Resample to project sample rate
    if sr_native != sr:
        harmonic = librosa.resample(harmonic, orig_sr=sr_native, target_sr=sr)

    log.info(f"[STEMS] Demucs separation complete, shape={harmonic.shape}")
    return harmonic


def stem_info() -> dict:
    """Return info about which separation method will be used."""
    if _demucs_available():
        return {"method": "demucs", "model": "htdemucs", "quality": "high"}
    return {"method": "hpss", "model": "librosa", "quality": "standard"}
