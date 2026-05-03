from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.routes import upload_router, analysis_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Analyze uploaded audio files and extract musical information.",
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",     # ReDoc
)

# ---------------------------------------------------------------------------
# CORS — allow Vue dev server to call the API during development
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
app.include_router(upload_router)   # POST /api/analysis/upload
app.include_router(analysis_router) # GET  /api/health, POST /api/export


@app.on_event("startup")
async def startup():
    """Create upload directory if it doesn't exist."""
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✅ {settings.APP_NAME} v{settings.APP_VERSION} running")
    print(f"   Upload dir : {settings.UPLOAD_DIR.resolve()}")
    print(f"   Docs       : http://localhost:8000/docs")
