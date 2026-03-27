from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.utils.logger import setup_logging
from app.api import agents_router, tasks_router
from app.orchestration import initialize_supervisor

# Setup logging
logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 HelixOS initializing...")
    init_db()
    logger.info("📦 Database initialized")
    
    initialize_supervisor()
    logger.info("🧠 Supervisor agent initialized")
    
    yield
    
    # Shutdown
    logger.info("🛑 HelixOS shutting down...")

app = FastAPI(
    title="HelixOS API",
    description="Enterprise OS for Autonomous AI Workforces",
    version="0.1.0",
    lifespan=lifespan
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://0.0.0.0:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost",
        "http://127.0.0.1",
        "http://0.0.0.0",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"🌐 {request.method} {request.url}")
    response = await call_next(request)
    return response


# Include routers
app.include_router(agents_router, prefix="/api/agents", tags=["agents"])
app.include_router(tasks_router, prefix="/api/tasks", tags=["tasks"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "HelixOS API",
        "version": "0.1.0",
        "environment": settings.ENVIRONMENT
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to HelixOS",
        "docs": "/docs",
        "api_version": "0.1.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.DEBUG)