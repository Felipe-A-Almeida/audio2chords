import numpy as np
import librosa
from backend.schemas.analysis import KeyResult


# ---------------------------------------------------------------------------
# Krumhansl-Schmuckler key profiles
# These 12-element vectors represent how well each pitch class "fits"
# a given major or minor key. Derived from music cognition experiments.
# ---------------------------------------------------------------------------
_MAJOR_PROFILE = np.array([
    6.35, 2.23, 3.48, 2.33, 4.38, 4.09,
    2.52, 5.19, 2.39, 3.66, 2.29, 2.88
])
_MINOR_PROFILE = np.array([
    6.33, 2.68, 3.52, 5.38, 2.60, 3.53,
    2.54, 4.75, 3.98, 2.69, 3.34, 3.17
])

_NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F',
               'F#', 'G', 'G#', 'A', 'A#', 'B']

# Enharmonic spellings that look better in a UI
_ENHARMONIC = {
    'C#': 'C#', 'D#': 'Eb', 'F#': 'F#', 'G#': 'Ab', 'A#': 'Bb'
}


def _prettify(note: str) -> str:
    return _ENHARMONIC.get(note, note)


def _correlate_profile(chroma_mean: np.ndarray, profile: np.ndarray) -> np.ndarray:
    """
    Compute Pearson correlation between the mean chroma vector and
    all 12 rotations of a key profile.
    Returns array of 12 correlation values (one per root note).
    """
    scores = np.zeros(12)
    for i in range(12):
        rotated = np.roll(profile, i)
        # Pearson r — normalise both vectors
        c = np.corrcoef(chroma_mean, rotated)[0, 1]
        scores[i] = c if not np.isnan(c) else 0.0
    return scores


def detect_key(y: np.ndarray, sr: int) -> KeyResult:
    """
    Estimate musical key using the Krumhansl-Schmuckler algorithm.

    Steps:
      1. Compute harmonic-only signal (remove percussion to reduce chroma noise)
      2. Build chromagram (Constant-Q chroma, more accurate than STFT chroma)
      3. Average chroma across time → 12-element pitch class distribution
      4. Correlate against all 24 key profiles (12 major + 12 minor)
      5. Pick best match; confidence = normalised margin over second-best
    """
    # Isolate harmonic content — chords/melody dominate, drums don't pollute chroma
    y_harm = librosa.effects.harmonic(y, margin=4.0)

    # Constant-Q chromagram: better frequency resolution than STFT at low pitches
    chroma = librosa.feature.chroma_cqt(y=y_harm, sr=sr, bins_per_octave=36)

    # Mean pitch class distribution across the whole track
    chroma_mean = np.mean(chroma, axis=1)   # shape: (12,)

    # Correlate against major and minor profiles for all 12 roots
    major_scores = _correlate_profile(chroma_mean, _MAJOR_PROFILE)
    minor_scores = _correlate_profile(chroma_mean, _MINOR_PROFILE)

    best_major_idx = int(np.argmax(major_scores))
    best_minor_idx = int(np.argmax(minor_scores))

    best_major_score = major_scores[best_major_idx]
    best_minor_score = minor_scores[best_minor_idx]

    # Pick the overall winner
    if best_major_score >= best_minor_score:
        root_idx = best_major_idx
        mode     = 'major'
        winner   = best_major_score
        all_scores = np.concatenate([major_scores, minor_scores])
    else:
        root_idx = best_minor_idx
        mode     = 'minor'
        winner   = best_minor_score
        all_scores = np.concatenate([major_scores, minor_scores])

    root = _NOTE_NAMES[root_idx]
    root_pretty = _prettify(root)
    label = f"{root_pretty} {mode}"

    # Confidence: how far ahead of the second-best candidate (across all 24 keys)
    sorted_scores = np.sort(all_scores)[::-1]
    margin = float(sorted_scores[0] - sorted_scores[1])
    # Margin of ~0.1 is already quite decisive; normalise to [0, 1]
    confidence = float(np.clip(margin / 0.15, 0.0, 1.0))

    print(f"[KEY] detected={label}  score={winner:.3f}  confidence={confidence:.2f}")
    print(f"      top major: {_NOTE_NAMES[best_major_idx]} ({best_major_score:.3f})  "
          f"top minor: {_NOTE_NAMES[best_minor_idx]} ({best_minor_score:.3f})")

    return KeyResult(
        key=root_pretty,
        mode=mode,
        label=label,
        confidence=round(confidence, 3),
    )
