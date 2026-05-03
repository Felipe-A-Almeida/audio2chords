"""
Chord detection via chromagram template matching.

Architecture:
  1. Extract harmonic signal
  2. Compute CQT chromagram with fine hop length
  3. Smooth chroma over time (removes transient noise)
  4. For each frame: correlate against 48 chord templates (major/minor × 12 roots + 7th)
  5. Merge consecutive identical chords into events
  6. Filter out very short segments (< 1 beat)

Accuracy note:
  This is a heuristic approach — it works well on recordings with clear
  harmonic content and simple progressions. Dense jazz voicings or heavily
  distorted guitars will degrade accuracy. For an MVP this gives musically
  meaningful output in most pop/rock/folk material.
"""

import numpy as np
from scipy.ndimage import median_filter
import librosa

from backend.schemas.analysis import ChordEvent
from backend.config import settings


# ---------------------------------------------------------------------------
# Chord templates — 12-dimensional binary chroma vectors
# Each vector marks which pitch classes (C=0 … B=11) belong to the chord.
# ---------------------------------------------------------------------------

def _build_templates() -> dict[str, np.ndarray]:
    """
    Build chord templates for all 12 roots × 4 qualities:
      - major triad   (root, M3, P5)
      - minor triad   (root, m3, P5)
      - dominant 7th  (root, M3, P5, m7)
      - minor 7th     (root, m3, P5, m7)

    Returns dict mapping chord name → 12-element float array.
    """
    ROOT_NAMES = ['C', 'C#', 'D', 'Eb', 'E', 'F',
                  'F#', 'G', 'Ab', 'A', 'Bb', 'B']

    # Intervals in semitones relative to root
    QUALITIES = {
        ''   : [0, 4, 7],          # major
        'm'  : [0, 3, 7],          # minor
        '7'  : [0, 4, 7, 10],      # dominant 7th
        'm7' : [0, 3, 7, 10],      # minor 7th
    }

    templates = {}
    for root_idx, root_name in enumerate(ROOT_NAMES):
        for quality, intervals in QUALITIES.items():
            vec = np.zeros(12)
            for interval in intervals:
                vec[(root_idx + interval) % 12] = 1.0
            # Normalize so dot-product == cosine similarity
            vec /= np.linalg.norm(vec)
            templates[f"{root_name}{quality}"] = vec

    return templates


_TEMPLATES = _build_templates()
_TEMPLATE_NAMES   = list(_TEMPLATES.keys())
_TEMPLATE_MATRIX  = np.stack(list(_TEMPLATES.values()), axis=0)  # (n_chords, 12)


# ---------------------------------------------------------------------------
# Enharmonic cleanup — prefer readable spellings in UI
# ---------------------------------------------------------------------------
_DISPLAY = {
    'C#': 'C#', 'C#m': 'C#m', 'C#7': 'C#7', 'C#m7': 'C#m7',
    'Eb': 'Eb', 'Ebm': 'D#m', 'Eb7': 'Eb7', 'Ebm7': 'D#m7',
    'F#': 'F#', 'F#m': 'F#m', 'F#7': 'F#7', 'F#m7': 'F#m7',
    'Ab': 'Ab', 'Abm': 'G#m', 'Ab7': 'Ab7', 'Abm7': 'G#m7',
    'Bb': 'Bb', 'Bbm': 'Bbm', 'Bb7': 'Bb7', 'Bbm7': 'Bbm7',
}

def _display_name(chord: str) -> str:
    return _DISPLAY.get(chord, chord)


# ---------------------------------------------------------------------------
# Main detection function
# ---------------------------------------------------------------------------

def detect_chords(y: np.ndarray, sr: int) -> list[ChordEvent]:
    """
    Detect chord progression and return a list of ChordEvent objects.

    Each event has: start_seconds, end_seconds, chord name, confidence.
    """
    hop_length = 2048   # ~93ms per frame at 22050 Hz — good temporal resolution
                        # without creating thousands of micro-segments

    # 1. Isolate harmonic content
    y_harm = librosa.effects.harmonic(y, margin=4.0)

    # 2. CQT chromagram
    chroma = librosa.feature.chroma_cqt(
        y=y_harm,
        sr=sr,
        hop_length=hop_length,
        bins_per_octave=36,     # finer pitch resolution
    )  # shape: (12, n_frames)

    # 3. Smooth over time with median filter to suppress transient noise
    #    Window of 9 frames ≈ 840ms — smooths out ornaments and transitions
    chroma_smooth = median_filter(chroma, size=(1, 9))

    # Normalize each frame to unit vector for cosine similarity
    norms = np.linalg.norm(chroma_smooth, axis=0, keepdims=True)
    norms = np.where(norms < 1e-6, 1.0, norms)   # avoid div-by-zero on silence
    chroma_norm = chroma_smooth / norms            # (12, n_frames)

    # 4. Score every frame against all chord templates (vectorised dot product)
    #    scores shape: (n_chords, n_frames)
    scores = _TEMPLATE_MATRIX @ chroma_norm        # (n_chords, n_frames)

    best_chord_idx  = np.argmax(scores, axis=0)    # (n_frames,)
    best_chord_conf = np.max(scores, axis=0)       # (n_frames,)

    # 5. Convert frame indices to seconds
    frame_times = librosa.frames_to_time(
        np.arange(len(best_chord_idx)),
        sr=sr,
        hop_length=hop_length,
    )
    duration = len(y) / sr

    # 6. Merge consecutive identical chords into segments
    raw_events = _merge_frames(
        chord_indices=best_chord_idx,
        confidences=best_chord_conf,
        times=frame_times,
        duration=duration,
    )

    # 7. Filter out very short segments (< 0.8s) — usually transients mis-labelled
    min_duration = max(0.8, settings.CHORD_HOP_SECONDS)
    events = [e for e in raw_events if (e['end'] - e['start']) >= min_duration]

    # If filtering removed everything, fall back to raw events
    if not events:
        events = raw_events

    print(f"[CHORDS] {len(events)} chord events detected")
    for e in events[:8]:   # log first 8
        print(f"  {e['start']:.1f}s–{e['end']:.1f}s  {e['chord']:<6}  conf={e['conf']:.2f}")
    if len(events) > 8:
        print(f"  … ({len(events) - 8} more)")

    return [
        ChordEvent(
            start_seconds=round(e['start'], 3),
            end_seconds=round(e['end'], 3),
            chord=_display_name(e['chord']),
            confidence=round(float(e['conf']), 3),
        )
        for e in events
    ]


def _merge_frames(
    chord_indices: np.ndarray,
    confidences: np.ndarray,
    times: np.ndarray,
    duration: float,
) -> list[dict]:
    """
    Collapse consecutive frames with the same chord into single events.
    Confidence for each event = mean confidence of its constituent frames.
    """
    if len(chord_indices) == 0:
        return []

    events = []
    current_chord = chord_indices[0]
    current_start = float(times[0])
    conf_accum    = [float(confidences[0])]

    for i in range(1, len(chord_indices)):
        if chord_indices[i] == current_chord:
            conf_accum.append(float(confidences[i]))
        else:
            events.append({
                'start': current_start,
                'end':   float(times[i]),
                'chord': _TEMPLATE_NAMES[current_chord],
                'conf':  float(np.mean(conf_accum)),
            })
            current_chord = chord_indices[i]
            current_start = float(times[i])
            conf_accum    = [float(confidences[i])]

    # Close the last segment
    events.append({
        'start': current_start,
        'end':   duration,
        'chord': _TEMPLATE_NAMES[current_chord],
        'conf':  float(np.mean(conf_accum)),
    })

    return events
