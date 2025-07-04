from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import Response, StreamingResponse
import httpx
import os

router = APIRouter()

# Get AI service URL from environment
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "https://restaurant-ai-ai-service.onrender.com")

async def proxy_request(request: Request, target_path: str) -> Response:
    """Proxy requests to AI service"""
    try:
        # Get request details
        method = request.method
        headers = dict(request.headers)
        
        # Remove hop-by-hop headers
        headers.pop('host', None)
        headers.pop('content-length', None)
        
        # Add internal service header to bypass rate limiting
        headers['X-Internal-Service'] = 'restaurant-service'
        print(f"DEBUG: Proxying to {target_path} with headers: {headers.get('X-Internal-Service')}")
        
        # Build target URL
        target_url = f"{AI_SERVICE_URL}{target_path}"
        
        # Get request body
        body = None
        if method in ['POST', 'PUT', 'PATCH']:
            body = await request.body()
        
        # Get query parameters
        query_params = dict(request.query_params)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=method,
                url=target_url,
                headers=headers,
                content=body,
                params=query_params
            )
            
            # Handle streaming responses (for audio)
            if response.headers.get('content-type', '').startswith('audio/'):
                return StreamingResponse(
                    iter([response.content]),
                    media_type=response.headers.get('content-type'),
                    headers={k: v for k, v in response.headers.items() if k.lower() not in ['content-length', 'transfer-encoding']}
                )
            
            # Regular response
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers={k: v for k, v in response.headers.items() if k.lower() not in ['content-length', 'transfer-encoding']},
                media_type=response.headers.get('content-type')
            )
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="AI service timeout")
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="AI service unavailable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proxy error: {str(e)}")

# Chat endpoints
@router.post("/restaurants/{restaurant_slug}/chat")
async def proxy_chat(restaurant_slug: str, request: Request):
    return await proxy_request(request, f"/api/v1/restaurants/{restaurant_slug}/chat")

@router.get("/restaurants/{restaurant_slug}/chat/suggestions")
async def proxy_chat_suggestions(restaurant_slug: str, request: Request):
    return await proxy_request(request, f"/api/v1/restaurants/{restaurant_slug}/chat/suggestions")

@router.post("/restaurants/{restaurant_slug}/chat/feedback")
async def proxy_chat_feedback(restaurant_slug: str, request: Request):
    return await proxy_request(request, f"/api/v1/restaurants/{restaurant_slug}/chat/feedback")

@router.get("/restaurants/{restaurant_slug}/chat/analytics")
async def proxy_chat_analytics(restaurant_slug: str, request: Request):
    return await proxy_request(request, f"/api/v1/restaurants/{restaurant_slug}/chat/analytics")

# Speech endpoints
@router.post("/speech/transcribe")
async def proxy_speech_transcribe(request: Request):
    return await proxy_request(request, "/api/v1/speech/transcribe")

@router.post("/speech/synthesize")
async def proxy_speech_synthesize(request: Request):
    return await proxy_request(request, "/api/v1/speech/synthesize")

@router.get("/speech/voices")
async def proxy_speech_voices(request: Request):
    return await proxy_request(request, "/api/v1/speech/voices")