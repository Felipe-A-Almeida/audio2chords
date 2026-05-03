# AudioChord 🎵

> Upload a track. Hear the theory.

AudioChord is a full-stack web application that analyzes audio files and extracts musical information in seconds. Upload an MP3 or WAV file and receive BPM, musical key, waveform, spectrogram, and a chord progression timeline.

Built as a portfolio-grade MVP demonstrating Python DSP engineering, clean API design, and a modern Vue 3 frontend.

![AudioChord](https://img.shields.io/badge/version-0.1.0-7C3AED?style=flat-square) ![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi&logoColor=white) ![Vue](https://img.shields.io/badge/Vue-3.4-4FC08D?style=flat-square&logo=vue.js&logoColor=white)

---

## Features

- **BPM Detection** — Beat tracking with percussive separation and autocorrelation-based confidence scoring
- **Key Detection** — Krumhansl-Schmuckler algorithm over CQT chromagram with harmonic isolation
- **Waveform** — RMS-envelope downsampling to 2000 points for accurate visual representation
- **Spectrogram** — Mel-scaled, dB-normalized heatmap (128 bands × 200 time frames)
- **Chord Timeline** — Template matching against 48 chord templates (major, minor, dom7, m7) across all 12 roots
- **JSON Export** — Full structured analysis result as a downloadable file
- **File Validation** — Format and size checks before any processing

---

## Tech Stack

### Backend
| Library | Role |
|---|---|
| **FastAPI** | HTTP API, routing, request validation |
| **Librosa** | Audio loading, beat tracking, chromagram, mel spectrogram |
| **NumPy / SciPy** | Signal processing, template matching, median filtering |
| **Pydantic** | Schema definition and serialization |
| **Uvicorn** | ASGI server |

### Frontend
| Library | Role |
|---|---|
| **Vue 3** | Reactive UI with Composition API |
| **Vite** | Dev server with API proxy, fast HMR |
| **TailwindCSS** | Utility-first styling |
| **Chart.js** | Waveform rendering |
| **Axios** | HTTP client with upload progress |

---

## Project Structure

```
audiochord/
├── backend/
│   ├── audio/                  # Pure DSP layer — no framework dependencies
│   │   ├── bpm.py              # Beat tracking with confidence scoring
│   │   ├── key.py              # Krumhansl-Schmuckler key detection
│   │   ├── waveform.py         # RMS-envelope downsampling
│   │   ├── spectrogram.py      # Mel spectrogram computation
│   │   └── chords.py           # Chromagram template matching
│   ├── routes/
│   │   ├── upload.py           # POST /api/analysis/upload
│   │   └── analysis.py         # GET /api/health · POST /api/export
│   ├── services/
│   │   ├── analysis_service.py # Pipeline orchestration
│   │   └── file_service.py     # Upload validation and persistence
│   ├── schemas/
│   │   └── analysis.py         # Pydantic models for request/response
│   ├── config.py               # Centralized settings (Pydantic Settings)
│   └── main.py                 # FastAPI app, CORS, startup
└── frontend/
    └── src/
        ├── pages/
        │   ├── UploadPage.vue  # Drag-and-drop upload with progress
        │   └── ResultsPage.vue # Full analysis dashboard
        ├── components/
        │   ├── charts/         # WaveformChart, SpectrogramChart, ChordTimeline
        │   └── ui/             # FileDropzone, ProgressBar, MetadataCard
        ├── composables/
        │   ├── useAudioUpload.js  # Upload state machine (idle→uploading→done|error)
        │   └── useAnalysis.js     # Derived display values from raw result
        └── utils/
            └── formatters.js   # Duration, file size, timestamp formatting
```

---

## Quick Start

### Prerequisites
- Python 3.12
- Node.js 18+

### Backend

```bash
cd audiochord/backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt

cd ..
uvicorn backend.main:app --reload
# → API running at http://localhost:8000
# → Swagger UI at http://localhost:8000/docs
```

### Frontend

```bash
cd audiochord/frontend
npm install
npm run dev
# → App running at http://localhost:5173
```

Open **http://localhost:5173**, upload an MP3 or WAV file, and receive your analysis.

---

## API Reference

### `POST /api/analysis/upload`

Upload an audio file and receive full musical analysis.

**Request:** `multipart/form-data` with field `file` (MP3 or WAV, max 50 MB)

**Response:**
```json
{
  "metadata": {
    "filename": "my_track.mp3",
    "format": "mp3",
    "duration_seconds": 213.4,
    "sample_rate": 44100,
    "channels": 2,
    "file_size_bytes": 8421376
  },
  "bpm": { "bpm": 124.0, "confidence": 0.87 },
  "key": { "key": "A", "mode": "minor", "label": "A minor", "confidence": 0.91 },
  "waveform": {
    "samples": [0.012, -0.034, ...],
    "duration_seconds": 213.4
  },
  "spectrogram": {
    "values": [[...], ...],
    "time_axis": [0.0, 0.1, ...],
    "frequency_axis": [0.0, 86.1, ...],
    "db_min": -72.4,
    "db_max": 0.0
  },
  "chords": [
    { "start_seconds": 0.0, "end_seconds": 12.3, "chord": "Am", "confidence": 0.84 },
    { "start_seconds": 12.3, "end_seconds": 24.1, "chord": "F", "confidence": 0.79 }
  ],
  "summary": "124.0 BPM · A minor"
}
```

### `GET /api/health`
Liveness probe. Returns `{ "status": "ok" }`.

### `POST /api/export`
Re-receives an `AnalysisResult` payload and returns it as a `Content-Disposition: attachment` JSON download.

---

## How It Works

### BPM Detection
1. Percussive component is isolated with `librosa.effects.percussive` (margin=3.0) to reduce confusion from sustained harmonic content
2. Onset strength envelope computed with median aggregation
3. Dynamic programming beat tracker finds global tempo and beat positions
4. Confidence derived from the normalized autocorrelation peak at the detected beat period — a rhythmically consistent signal produces a sharp peak

### Key Detection (Krumhansl-Schmuckler)
1. Harmonic signal isolated with `librosa.effects.harmonic` (margin=4.0) to reduce drum/noise interference
2. Constant-Q chromagram computed (`chroma_cqt`, `bins_per_octave=36`) for better low-frequency resolution than STFT
3. Mean pitch-class distribution computed across the full track
4. Pearson correlation computed between the chroma vector and all 24 key profiles (12 major + 12 minor) based on Krumhansl's music cognition research
5. Confidence = normalized margin between the top and second-best candidate across all 24 keys

### Chord Detection
1. Harmonic signal isolated (same as key detection)
2. CQT chromagram with `hop_length=2048` (~93ms per frame)
3. Median filter applied over 9-frame window (~840ms) to suppress transient noise and ornaments
4. Each frame scored against 48 chord templates (major, minor, dom7, m7 in all 12 roots) via cosine similarity
5. Consecutive frames with identical best-match chord merged into single events
6. Segments shorter than 0.8s filtered out (likely mis-labelled transients)

### Waveform
RMS amplitude computed per frame across 2000 equally-spaced windows, then normalized to [-1, 1]. This preserves the true amplitude envelope unlike naive decimation.

### Spectrogram
Mel-scaled spectrogram converted to dB relative to peak (`power_to_db`), then downsampled to 200 time frames for a manageable JSON payload. Mel scale approximates human auditory perception.

---

## Configuration

All settings live in `backend/config.py` and can be overridden via a `.env` file:

| Variable | Default | Description |
|---|---|---|
| `MAX_FILE_SIZE_MB` | `50` | Maximum upload size |
| `SAMPLE_RATE` | `22050` | Librosa resampling rate |
| `WAVEFORM_POINTS` | `2000` | Output waveform resolution |
| `SPECTROGRAM_BINS` | `128` | Mel frequency bands |
| `CHORD_HOP_SECONDS` | `0.5` | Minimum chord segment duration |
| `CORS_ORIGINS` | `localhost:5173` | Allowed frontend origins |

---

## Limitations & Roadmap

**Current limitations (expected for v0.1.0):**
- Chord detection accuracy degrades on heavily distorted guitars, complex jazz voicings, and recordings with high reverb
- Key detection on atonal or modal music may produce low-confidence results
- No audio playback in the UI
- Analysis results are not persisted between sessions

**Potential v0.2.0 improvements:**
- ML-based chord recognition (madmom, or a trained CNN) for higher accuracy
- Audio playback with WaveSurfer.js, cursor synced to chord timeline
- SQLite persistence to avoid reprocessing the same file
- Additional format support (FLAC, OGG, M4A) via ffmpeg
- Stem separation with Demucs before analysis

---

## License

MIT

**Planned v0.3.0 — Interactive Chord Diagrams:**
- Piano keyboard diagram (SVG) with chord tones highlighted per chord event
- Guitar fretboard diagram (SVG) with fingering positions from a static voicing dictionary
- Audio playback in the browser (Web Audio API or HTMLAudioElement), with the original file held in memory after upload
- Chord diagrams animate in sync with playback — current chord highlighted as the track plays, driven by `requestAnimationFrame` comparing `audio.currentTime` against the chord timeline's `start_seconds`/`end_seconds` events
- Voicing dictionary shipped as a static JSON in the frontend (~200 common chords) — no backend changes needed for diagram rendering
