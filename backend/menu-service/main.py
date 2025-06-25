from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import sys
import logging

# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from database.connection import init_database, check_database_health
from routers import menu, ingredients
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
    logger.info("Starting Menu Service...")
    try:
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Menu Service...")

# Create FastAPI application
app = FastAPI(
    title="Menu Service",
    description="Menu and ingredient management service for the Restaurant AI Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS - nginx handles it in development, backend handles it in production
import os
if os.getenv("RENDER"):  # Only add CORS on Render (production)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://restaurant-ai-frontend.onrender.com", "http://localhost:3000", "http://localhost:5173"],
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
app.include_router(menu.router, prefix="/api/v1", tags=["menu"])
app.include_router(ingredients.router, prefix="/api/v1", tags=["ingredients"])

# Serve static files for uploaded images
uploads_dir = os.path.join(os.getcwd(), "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Menu Service",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    database_healthy = check_database_health()
    
    return {
        "status": "healthy" if database_healthy else "unhealthy",
        "timestamp": "2024-01-15T10:00:00Z",
        "version": "1.0.0",
        "services": {
            "database": database_healthy,
            "redis": database_healthy
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