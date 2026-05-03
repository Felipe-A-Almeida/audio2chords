"""
Lightweight SQLite persistence layer using aiosqlite.

Schema:
  analyses(id, filename, format, created_at, result_json)

  - id          : UUID string (primary key, also used as the audio file_id)
  - filename    : original uploaded filename
  - format      : mp3 | wav
  - created_at  : ISO timestamp
  - result_json : full AnalysisResult serialized as JSON text

The audio file is stored at uploads/<id>.<ext> and served via
GET /api/audio/<id>. This way the frontend can play the track
and we avoid reprocessing the same content.
"""

import json
import aiosqlite
from pathlib import Path
from backend.config import settings

DB_PATH = Path("audiochord.db")


async def init_db() -> None:
    """Create tables if they don't exist. Called on FastAPI startup."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id           TEXT PRIMARY KEY,
                filename     TEXT NOT NULL,
                format       TEXT NOT NULL,
                created_at   TEXT NOT NULL,
                result_json  TEXT NOT NULL
            )
        """)
        await db.commit()
    print(f"[DB] Initialized at {DB_PATH.resolve()}")


async def save_analysis(analysis_id: str, filename: str, fmt: str, result_dict: dict) -> None:
    """Persist a completed analysis result."""
    from datetime import datetime, timezone
    created = datetime.now(timezone.utc).isoformat()

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO analyses (id, filename, format, created_at, result_json)"
            " VALUES (?, ?, ?, ?, ?)",
            (analysis_id, filename, fmt, created, json.dumps(result_dict))
        )
        await db.commit()


async def load_analysis(analysis_id: str) -> dict | None:
    """Retrieve a previously saved analysis. Returns None if not found."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT result_json FROM analyses WHERE id = ?", (analysis_id,)
        ) as cursor:
            row = await cursor.fetchone()
    return json.loads(row[0]) if row else None


async def list_analyses(limit: int = 20) -> list[dict]:
    """Return recent analyses for a history view (id, filename, created_at, format)."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT id, filename, format, created_at FROM analyses"
            " ORDER BY created_at DESC LIMIT ?",
            (limit,)
        ) as cursor:
            rows = await cursor.fetchall()
    return [
        {"id": r[0], "filename": r[1], "format": r[2], "created_at": r[3]}
        for r in rows
    ]
