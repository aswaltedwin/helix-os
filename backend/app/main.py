from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.utils.logger import setup_logging
from app.api import agents, tasks
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
        "http://localhost"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])

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