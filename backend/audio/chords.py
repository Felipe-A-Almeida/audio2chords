import numpy as np
from scipy.ndimage import median_filter
import librosa
from backend.schemas.analysis import ChordEvent
from backend.audio.stems import StemResult
from backend.config import settings


def _build_templates():
    ROOT_NAMES = ['C','C#','D','Eb','E','F','F#','G','Ab','A','Bb','B']
    QUALITIES  = {'':[0,4,7],'m':[0,3,7],'7':[0,4,7,10],'m7':[0,3,7,10]}
    templates  = {}
    for root_idx, root_name in enumerate(ROOT_NAMES):
        for quality, intervals in QUALITIES.items():
            vec = np.zeros(12)
            for interval in intervals:
                vec[(root_idx + interval) % 12] = 1.0
            vec /= np.linalg.norm(vec)
            templates[f"{root_name}{quality}"] = vec
    return templates

_TEMPLATES       = _build_templates()
_TEMPLATE_NAMES  = list(_TEMPLATES.keys())
_TEMPLATE_MATRIX = np.stack(list(_TEMPLATES.values()), axis=0)

_DISPLAY = {
    'C#':'C#','C#m':'C#m','C#7':'C#7','C#m7':'C#m7',
    'Eb':'Eb','Ebm':'D#m','Eb7':'Eb7','Ebm7':'D#m7',
    'F#':'F#','F#m':'F#m','F#7':'F#7','F#m7':'F#m7',
    'Ab':'Ab','Abm':'G#m','Ab7':'Ab7','Abm7':'G#m7',
    'Bb':'Bb','Bbm':'Bbm','Bb7':'Bb7','Bbm7':'Bbm7',
}
def _display_name(chord): return _DISPLAY.get(chord, chord)


def detect_chords(y: np.ndarray, sr: int, stems: StemResult | None = None) -> list[ChordEvent]:
    """
    Chord detection via chromagram template matching.
    v0.4.2: uses harmonic stem from StemResult when available.
    """
    hop_length = 2048

    if stems is not None:
        y_harm = stems.harmonic
    else:
        y_harm = librosa.effects.harmonic(y, margin=4.0)

    chroma        = librosa.feature.chroma_cqt(y=y_harm, sr=sr,
                      hop_length=hop_length, bins_per_octave=36)
    chroma_smooth = median_filter(chroma, size=(1, 9))
    norms         = np.linalg.norm(chroma_smooth, axis=0, keepdims=True)
    norms         = np.where(norms < 1e-6, 1.0, norms)
    chroma_norm   = chroma_smooth / norms

    scores          = _TEMPLATE_MATRIX @ chroma_norm
    best_chord_idx  = np.argmax(scores, axis=0)
    best_chord_conf = np.max(scores, axis=0)

    frame_times = librosa.frames_to_time(
        np.arange(len(best_chord_idx)), sr=sr, hop_length=hop_length,
    )
    duration   = len(y) / sr
    raw_events = _merge_frames(best_chord_idx, best_chord_conf, frame_times, duration)
    min_dur    = max(0.8, settings.CHORD_HOP_SECONDS)
    events     = [e for e in raw_events if (e['end'] - e['start']) >= min_dur] or raw_events

    print(f"[CHORDS] {len(events)} chord events detected")
    for e in events[:8]:
        print(f"  {e['start']:.1f}s–{e['end']:.1f}s  {e['chord']:<6}  conf={e['conf']:.2f}")

    return [
        ChordEvent(
            start_seconds=round(e['start'], 3),
            end_seconds=round(e['end'], 3),
            chord=_display_name(e['chord']),
            confidence=round(float(e['conf']), 3),
        )
        for e in events
    ]


def _merge_frames(chord_indices, confidences, times, duration):
    if not len(chord_indices): return []
    events, current = [], chord_indices[0]
    start, accum = float(times[0]), [float(confidences[0])]
    for i in range(1, len(chord_indices)):
        if chord_indices[i] == current:
            accum.append(float(confidences[i]))
        else:
            events.append({'start':start,'end':float(times[i]),
                           'chord':_TEMPLATE_NAMES[current],'conf':float(np.mean(accum))})
            current, start, accum = chord_indices[i], float(times[i]), [float(confidences[i])]
    events.append({'start':start,'end':duration,
                   'chord':_TEMPLATE_NAMES[current],'conf':float(np.mean(accum))})
    return events
