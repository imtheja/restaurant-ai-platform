from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import os
import sys
import logging

# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from database.connection import init_database, check_database_health
from routers import chat, conversations, speech
from middleware import rate_limiting, request_logging, error_handling

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting AI Service...")
    try:
        init_database()
        logger.info("Database initialized successfully")
        
        # Verify OpenAI API key
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            logger.warning("OPENAI_API_KEY not set - AI features will be limited")
        else:
            logger.info("OpenAI API key configured")
            
    except Exception as e:
        logger.error(f"Failed to initialize AI service: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Service...")

# Create FastAPI application
app = FastAPI(
    title="AI Service",
    description="AI conversation and recommendation service for the Restaurant AI Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# Add custom middleware
app.middleware("http")(request_logging.log_requests)
app.middleware("http")(rate_limiting.rate_limit_middleware)
app.middleware("http")(error_handling.global_exception_handler)

# Include routers
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(conversations.router, prefix="/api/v1", tags=["conversations"])
app.include_router(speech.router, prefix="/api/v1", tags=["speech"])

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "AI Service",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    database_healthy = check_database_health()
    openai_configured = bool(os.getenv("OPENAI_API_KEY"))
    
    return {
        "status": "healthy" if database_healthy and openai_configured else "unhealthy",
        "timestamp": "2024-01-15T10:00:00Z",
        "version": "1.0.0",
        "services": {
            "database": database_healthy,
            "redis": database_healthy,
            "openai": openai_configured
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("DEBUG", "false").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )