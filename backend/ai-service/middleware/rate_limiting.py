from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
import sys
import os

# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from database.connection import get_redis
from utils import get_client_ip, rate_limit_key, config

async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limiting middleware to prevent abuse.
    """
    # Skip rate limiting for health checks and docs
    if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)
    
    # Skip rate limiting for internal service calls
    # Check for internal service header or specific user agents
    user_agent = request.headers.get("User-Agent", "")
    internal_service_header = request.headers.get("X-Internal-Service")
    
    # Check if request is from restaurant service (internal proxy)
    if internal_service_header or "restaurant-ai-" in user_agent:
        print(f"DEBUG: Skipping rate limit - Internal service: {internal_service_header}, User-Agent: {user_agent}")
        return await call_next(request)
    
    # Check if on Render and request is from another Render service
    if os.getenv("RENDER"):
        forwarded_for = request.headers.get("X-Forwarded-For", "")
        # Render internal IPs typically start with 10.x.x.x
        if forwarded_for.startswith("10."):
            return await call_next(request)
    
    redis_client = get_redis()
    if not redis_client:
        # If Redis is not available, allow the request
        return await call_next(request)
    
    # Get client identifier
    client_ip = get_client_ip(request)
    rate_limit_per_minute = config.get('rate_limit_per_minute', 100)
    
    # Create rate limiting key
    key = rate_limit_key(client_ip, "1min")
    
    try:
        # Get current count
        current_count = redis_client.get(key)
        
        if current_count is None:
            # First request in this window
            redis_client.setex(key, 60, 1)
        else:
            current_count = int(current_count)
            
            if current_count >= rate_limit_per_minute:
                # Rate limit exceeded
                return JSONResponse(
                    status_code=429,
                    content={
                        "success": False,
                        "message": "Rate limit exceeded. Please try again later.",
                        "errors": ["Too many requests"]
                    },
                    headers={"Retry-After": "60"}
                )
            
            # Increment count
            redis_client.incr(key)
        
        # Add rate limiting headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(rate_limit_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(max(0, rate_limit_per_minute - int(current_count or 0) - 1))
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)
        
        return response
        
    except Exception as e:
        # If rate limiting fails, allow the request
        return await call_next(request)