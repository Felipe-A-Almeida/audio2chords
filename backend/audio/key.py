import numpy as np
import librosa
from backend.schemas.analysis import KeyResult
from backend.audio.stems import separate_harmonic

_MAJOR_PROFILE = np.array([
    6.35, 2.23, 3.48, 2.33, 4.38, 4.09,
    2.52, 5.19, 2.39, 3.66, 2.29, 2.88
])
_MINOR_PROFILE = np.array([
    6.33, 2.68, 3.52, 5.38, 2.60, 3.53,
    2.54, 4.75, 3.98, 2.69, 3.34, 3.17
])
_NOTE_NAMES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
_ENHARMONIC = {'C#':'C#','D#':'Eb','F#':'F#','G#':'Ab','A#':'Bb'}

def _prettify(note): return _ENHARMONIC.get(note, note)

def _correlate_profile(chroma_mean, profile):
    scores = np.zeros(12)
    for i in range(12):
        rotated = np.roll(profile, i)
        c = np.corrcoef(chroma_mean, rotated)[0, 1]
        scores[i] = c if not np.isnan(c) else 0.0
    return scores


def detect_key(y: np.ndarray, sr: int, audio_path=None) -> KeyResult:
    """
    Estimate musical key using Krumhansl-Schmuckler algorithm.
    Uses stem separation (Demucs if available, HPSS fallback) for
    cleaner chroma — better accuracy on vocals-heavy recordings.
    """
    # Use stem separation instead of raw harmonic() — cleaner chroma
    y_harm = separate_harmonic(y, sr, audio_path)

    chroma = librosa.feature.chroma_cqt(y=y_harm, sr=sr, bins_per_octave=36)
    chroma_mean = np.mean(chroma, axis=1)

    major_scores = _correlate_profile(chroma_mean, _MAJOR_PROFILE)
    minor_scores = _correlate_profile(chroma_mean, _MINOR_PROFILE)

    best_major_idx   = int(np.argmax(major_scores))
    best_minor_idx   = int(np.argmax(minor_scores))
    best_major_score = major_scores[best_major_idx]
    best_minor_score = minor_scores[best_minor_idx]

    if best_major_score >= best_minor_score:
        root_idx, mode, winner = best_major_idx, 'major', best_major_score
    else:
        root_idx, mode, winner = best_minor_idx, 'minor', best_minor_score

    all_scores = np.concatenate([major_scores, minor_scores])
    sorted_scores = np.sort(all_scores)[::-1]
    margin = float(sorted_scores[0] - sorted_scores[1])
    confidence = float(np.clip(margin / 0.15, 0.0, 1.0))

    root_pretty = _prettify(_NOTE_NAMES[root_idx])
    label = f"{root_pretty} {mode}"

    print(f"[KEY] detected={label}  score={winner:.3f}  confidence={confidence:.2f}")
    return KeyResult(key=root_pretty, mode=mode, label=label,
                     confidence=round(confidence, 3))
