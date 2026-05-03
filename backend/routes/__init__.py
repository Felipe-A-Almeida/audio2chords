# Re-export routers so main.py can do:
#   from backend.routes import upload_router, analysis_router
from backend.routes.upload import router as upload_router
from backend.routes.analysis import router as analysis_router
