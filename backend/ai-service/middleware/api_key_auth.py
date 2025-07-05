from fastapi import Request, HTTPException
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse
import os
import sys

# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from utils import config

# Optional API key authentication
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def validate_api_key(request: Request) -> bool:
    """
    Validate API key if required.
    Returns True if valid or not required, False otherwise.
    """
    # Get configured API keys
    internal_api_key = os.getenv("INTERNAL_API_KEY")
    
    # If no API key is configured, skip validation
    if not internal_api_key:
        return True
    
    # Get API key from request
    api_key = request.headers.get("X-API-Key")
    
    # Check if it's an internal service call with valid API key
    if api_key and api_key == internal_api_key:
        return True
    
    # Check if it's from an internal service (fallback)
    internal_service = request.headers.get("X-Internal-Service")
    if internal_service:
        return True
    
    return False

async def api_key_middleware(request: Request, call_next):
    """
    API key authentication middleware for production environments.
    """
    # Skip auth for health checks and docs
    if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json", "/"]:
        return await call_next(request)
    
    # Only enforce API key in production (Render)
    if os.getenv("RENDER"):
        if not await validate_api_key(request):
            return JSONResponse(
                status_code=401,
                content={
                    "success": False,
                    "message": "Invalid or missing API key",
                    "errors": ["Authentication required"]
                }
            )
    
    return await call_next(request)