from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.routes import upload_router, analysis_router
from backend.db import init_db

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Analyze uploaded audio files and extract musical information.",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(analysis_router)


@app.on_event("startup")
async def startup():
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    await init_db()
    print(f"✅ {settings.APP_NAME} v{settings.APP_VERSION} running")
    print(f"   Upload dir : {settings.UPLOAD_DIR.resolve()}")
    print(f"   Docs       : http://localhost:8000/docs")
