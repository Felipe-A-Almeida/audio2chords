import io
from midiutil import MIDIFile
from backend.schemas.analysis import AnalysisResult

_ROOT_SEMITONES: dict[str, int] = {
    'C': 0, 'C#': 1, 'Db': 1,
    'D': 2, 'D#': 3, 'Eb': 3,
    'E': 4,
    'F': 5, 'F#': 6, 'Gb': 6,
    'G': 7, 'G#': 8, 'Ab': 8,
    'A': 9, 'A#': 10, 'Bb': 10,
    'B': 11,
}

_QUALITY_INTERVALS: dict[str, list[int]] = {
    '':    [0, 4, 7],
    'm':   [0, 3, 7],
    '7':   [0, 4, 7, 10],
    'm7':  [0, 3, 7, 10],
    'maj7':[0, 4, 7, 11],
    'dim': [0, 3, 6],
    'aug': [0, 4, 8],
    'sus2':[0, 2, 7],
    'sus4':[0, 5, 7],
}

_BASE_MIDI = 48  # C3 — sits comfortably in mid-range for DAW import


def _parse_chord(chord_str: str) -> list[int] | None:
    """Return MIDI note numbers for a chord string, or None for unknown/silence."""
    if not chord_str or chord_str in ('N', 'X', 'None', 'silence'):
        return None

    # Split root (1-2 chars) from quality suffix
    root = None
    quality = ''
    for length in (2, 1):
        candidate = chord_str[:length]
        if candidate in _ROOT_SEMITONES:
            root = candidate
            quality = chord_str[length:]
            break

    if root is None:
        return None

    semitone = _ROOT_SEMITONES[root]
    intervals = _QUALITY_INTERVALS.get(quality, _QUALITY_INTERVALS[''])
    return [_BASE_MIDI + semitone + i for i in intervals]


def build_midi(result: AnalysisResult) -> bytes:
    """Convert an AnalysisResult into a MIDI file and return its raw bytes."""
    bpm = result.bpm.bpm
    chords = result.chords

    midi = MIDIFile(1, deinterleave=False)
    track, channel = 0, 0
    midi.addTempo(track, 0, bpm)

    # Key signature (best-effort: MIDIUtil uses sharps/flats count)
    _add_key_signature(midi, track, result.key.key, result.key.mode)

    velocity = 80

    for event in chords:
        notes = _parse_chord(event.chord)
        if not notes:
            continue

        start_beat = _seconds_to_beats(event.start_seconds, bpm)
        dur_beats  = _seconds_to_beats(event.end_seconds - event.start_seconds, bpm)
        dur_beats  = max(dur_beats, 0.25)  # minimum 1/16th note

        for pitch in notes:
            midi.addNote(track, channel, pitch, start_beat, dur_beats, velocity)

    buf = io.BytesIO()
    midi.writeFile(buf)
    return buf.getvalue()


def _seconds_to_beats(seconds: float, bpm: float) -> float:
    return seconds * bpm / 60.0


_KEY_SHARPS_FLATS = {
    'C': 0, 'G': 1, 'D': 2, 'A': 3, 'E': 4, 'B': 5, 'F#': 6,
    'F': -1, 'Bb': -2, 'Eb': -3, 'Ab': -4, 'Db': -5, 'Gb': -6,
    'D#': 3, 'G#': 4, 'C#': 7,
}


def _add_key_signature(midi: MIDIFile, track: int, key: str, mode: str) -> None:
    try:
        accidentals = _KEY_SHARPS_FLATS.get(key, 0)
        minor = 1 if mode.lower() in ('minor', 'min') else 0
        midi.addKeySignature(track, 0, accidentals, minor)
    except Exception:
        pass
