from fastapi import Request
import time
import logging
import uuid
import sys
import os

# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from utils import get_client_ip

# Configure logging
logger = logging.getLogger("restaurant_service.requests")

async def log_requests(request: Request, call_next):
    """
    Middleware to log all incoming requests and their responses.
    """
    # Generate request ID
    request_id = str(uuid.uuid4())[:8]
    
    # Start timing
    start_time = time.time()
    
    # Get client information
    client_ip = get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "Unknown")
    
    # Log request
    logger.info(
        f"[{request_id}] {request.method} {request.url.path} - "
        f"Client: {client_ip} - User-Agent: {user_agent[:100]}"
    )
    
    # Process request
    try:
        response = await call_next(request)
        
        # Calculate processing time
        process_time = (time.time() - start_time) * 1000
        
        # Log response
        logger.info(
            f"[{request_id}] Response: {response.status_code} - "
            f"Time: {process_time:.2f}ms"
        )
        
        # Add headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        
        return response
        
    except Exception as e:
        # Calculate processing time for errors
        process_time = (time.time() - start_time) * 1000
        
        # Log error
        logger.error(
            f"[{request_id}] Error: {str(e)} - Time: {process_time:.2f}ms"
        )
        
        # Re-raise the exception
        raise