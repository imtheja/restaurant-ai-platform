from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, OperationalError
import logging
import traceback
import sys
import os

# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from utils import create_error_response

# Configure logging
logger = logging.getLogger("restaurant_service.errors")

async def global_exception_handler(request: Request, call_next):
    """
    Global exception handler middleware.
    """
    try:
        response = await call_next(request)
        return response
        
    except HTTPException as e:
        # HTTP exceptions should be passed through
        raise e
        
    except RequestValidationError as e:
        # Validation errors
        logger.warning(f"Validation error on {request.url.path}: {str(e)}")
        
        errors = []
        for error in e.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            errors.append(f"{field}: {error['msg']}")
        
        return JSONResponse(
            status_code=422,
            content=create_error_response(
                message="Validation failed",
                errors=errors
            )
        )
        
    except IntegrityError as e:
        # Database integrity errors
        logger.error(f"Database integrity error on {request.url.path}: {str(e)}")
        
        # Check for specific constraint violations
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        
        if "unique constraint" in error_msg.lower():
            return JSONResponse(
                status_code=409,
                content=create_error_response(
                    message="Resource already exists",
                    errors=["A resource with this identifier already exists"]
                )
            )
        elif "foreign key constraint" in error_msg.lower():
            return JSONResponse(
                status_code=400,
                content=create_error_response(
                    message="Invalid reference",
                    errors=["Referenced resource does not exist"]
                )
            )
        else:
            return JSONResponse(
                status_code=400,
                content=create_error_response(
                    message="Database constraint violation",
                    errors=["The operation violates data integrity rules"]
                )
            )
            
    except OperationalError as e:
        # Database connection errors
        logger.error(f"Database operational error on {request.url.path}: {str(e)}")
        
        return JSONResponse(
            status_code=503,
            content=create_error_response(
                message="Service temporarily unavailable",
                errors=["Database connection issue. Please try again later."]
            )
        )
        
    except ValueError as e:
        # Value errors (usually from invalid UUIDs, etc.)
        logger.warning(f"Value error on {request.url.path}: {str(e)}")
        
        return JSONResponse(
            status_code=400,
            content=create_error_response(
                message="Invalid input value",
                errors=[str(e)]
            )
        )
        
    except Exception as e:
        # Unexpected errors
        logger.error(
            f"Unexpected error on {request.url.path}: {str(e)}\n"
            f"Traceback: {traceback.format_exc()}"
        )
        
        # In production, don't expose internal error details
        if os.getenv("DEBUG", "false").lower() == "true":
            error_detail = str(e)
        else:
            error_detail = "An unexpected error occurred"
        
        return JSONResponse(
            status_code=500,
            content=create_error_response(
                message="Internal server error",
                errors=[error_detail]
            )
        )