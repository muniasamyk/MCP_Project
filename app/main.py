from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import router as api_router
from app.utils.logger import get_logger

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info(f"Booting up {settings.APP_NAME}...")
    yield
    # Shutdown logic
    logger.info("Gracefully shutting down...")

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="MCP Agent API - POC",
        version="1.0.0",
        docs_url="/docs",
        redoc_url=None, # Disable redoc to keep it clean
        lifespan=lifespan,
    )

    # Configurable CORS
    # In production, we restrict this to specific domains
    allowed_origins = settings.ALLOWED_ORIGINS.split(",") if settings.ALLOWED_ORIGINS else []
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST"], # We only really need these
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api/v1")

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    # Hot reload enabled only if DEBUG is True
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
