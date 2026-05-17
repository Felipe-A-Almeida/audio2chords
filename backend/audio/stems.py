import numpy as np, logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

log = logging.getLogger(__name__)

class StemMode(str, Enum):
    HARMONIC     = "harmonic"
    INSTRUMENTAL = "instrumental"
    FULL         = "full"

@dataclass
class StemResult:
    harmonic:   np.ndarray
    percussive: np.ndarray
    method:     str = "hpss"
    model:      str = "librosa"
    quality:    str = "standard"
    mode:       str = "harmonic"
    vocals:     np.ndarray | None = None
    bass:       np.ndarray | None = None
    drums:      np.ndarray | None = None
    other:      np.ndarray | None = None

def separate(y, sr, audio_path=None, mode=StemMode.HARMONIC):
    if mode == StemMode.FULL:
        return StemResult(harmonic=y, percussive=y,
                          method="none", model="none", quality="none", mode="full")
    if _demucs_available() and audio_path is not None:
        try:
            return _separate_demucs(audio_path, sr, mode)
        except Exception as e:
            log.warning(f"[STEMS] Demucs failed ({e}), falling back to HPSS")
    if mode == StemMode.INSTRUMENTAL:
        log.warning("[STEMS] INSTRUMENTAL requested but Demucs not installed. Using HPSS.")
    return _separate_hpss(y, mode)

def save_harmonic_stem(result, sr, dest):
    import soundfile as sf
    sf.write(str(dest), result.harmonic, sr, subtype="PCM_16")
    return dest

def stem_info(mode=StemMode.HARMONIC):
    demucs = _demucs_available()
    return {
        "method": "demucs" if demucs else "hpss",
        "model":  "htdemucs" if demucs else "librosa",
        "quality": "high" if demucs else "standard",
        "mode": mode.value if (demucs or mode != StemMode.INSTRUMENTAL) else "harmonic",
        "demucs_available": demucs,
        "vocal_removal": mode == StemMode.INSTRUMENTAL and demucs,
    }

def _demucs_available():
    try:
        import demucs; return True
    except ImportError:
        return False

def _separate_hpss(y, mode):
    import librosa
    y_harm, y_perc = librosa.effects.hpss(y, margin=6.0)
    return StemResult(harmonic=y_harm, percussive=y_perc,
                      method="hpss", model="librosa", quality="standard", mode="harmonic")

def _separate_demucs(audio_path, sr, mode):
    import torch, librosa
    from demucs.pretrained import get_model
    from demucs.apply import apply_model
    model = get_model("htdemucs"); model.eval()
    y_native, sr_native = librosa.load(str(audio_path), sr=None, mono=False)
    if y_native.ndim == 1: y_native = np.stack([y_native, y_native])
    wav = torch.tensor(y_native, dtype=torch.float32).unsqueeze(0)
    with torch.no_grad():
        sources = apply_model(model, wav, device="cpu", progress=False)
    def to_mono(t):
        a = t.mean(0).numpy()
        return librosa.resample(a, orig_sr=sr_native, target_sr=sr) if sr_native != sr else a
    drums=to_mono(sources[0,0]); bass=to_mono(sources[0,1])
    other=to_mono(sources[0,2]); vocals=to_mono(sources[0,3])
    harmonic = (other+bass*0.5)/1.5 if mode==StemMode.INSTRUMENTAL else (other+vocals)/2.0
    return StemResult(harmonic=harmonic, percussive=drums, method="demucs",
                      model="htdemucs", quality="high", mode=mode.value,
                      vocals=vocals, bass=bass, drums=drums, other=other)
