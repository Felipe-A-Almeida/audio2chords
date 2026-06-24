from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from backend.config import settings
from backend.routes import upload_router, analysis_router
from backend.db import init_db

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Analyze uploaded audio files and extract musical information.",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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
