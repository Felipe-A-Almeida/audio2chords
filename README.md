# AudioChord 🎵

Analyze uploaded audio files and extract musical information.

## Quick start

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
# → http://localhost:8000/docs
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

## Stack
- **Backend**: Python 3.12 · FastAPI · Librosa · NumPy · SciPy
- **Frontend**: Vue 3 · Vite · TailwindCSS · Chart.js
