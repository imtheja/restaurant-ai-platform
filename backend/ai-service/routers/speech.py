from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.orm import Session
import openai
import io
import os
import sys
from typing import Optional
import tempfile

# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from database.connection import get_db
from schemas import APIResponse
from utils import create_success_response, create_error_response

router = APIRouter()

class SpeechService:
    def __init__(self):
        # OpenAI API configuration (standardized to use only OpenAI)
        api_key = os.getenv("OPENAI_API_KEY")
        
        # Check text-only mode
        self.text_only_mode = os.getenv("TEXT_ONLY_MODE", "false").lower() == "true"
        
        # Check if we have a valid API key (not development placeholder)
        self.api_key_available = bool(
            api_key and 
            not api_key.startswith("your_") and 
            api_key != "sk-fake-key-for-development-only" and
            len(api_key) > 20  # Reasonable check for real API keys
        )
        
        if self.api_key_available:
            self.openai_client = openai.OpenAI(api_key=api_key)
        else:
            self.openai_client = None
    
    async def transcribe_audio(self, audio_file: UploadFile) -> str:
        """Transcribe audio using OpenAI Whisper"""
        if not self.api_key_available:
            # Fallback: return mock transcription for development
            return "Hello, this is a mock transcription since OpenAI API key is not configured."
        
        try:
            # Create a temporary file to store the uploaded audio
            with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_file:
                content = await audio_file.read()
                temp_file.write(content)
                temp_file.flush()
                
                # Use OpenAI Whisper API for transcription
                with open(temp_file.name, 'rb') as audio:
                    transcript = self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio,
                        language="en"  # Can be made dynamic based on restaurant settings
                    )
                
                # Clean up temp file
                os.unlink(temp_file.name)
                
                return transcript.text
        
        except Exception as e:
            # Clean up temp file if it exists
            if 'temp_file' in locals():
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
            raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    
    async def generate_speech(self, text: str, voice: str = "alloy") -> bytes:
        """Generate speech using OpenAI TTS"""
        # Return silent audio if in text-only mode
        if self.text_only_mode:
            # Return minimal silent MP3 file
            silent_mp3 = b'\xff\xfb\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            return silent_mp3
            
        if not self.api_key_available:
            # Fallback: return a very short silent audio file for development
            # This is a minimal MP3 file (silent, 1 second)
            silent_mp3 = b'\xff\xfb\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            return silent_mp3
        
        try:
            # Clean text for speech synthesis
            clean_text = text.strip()
            if not clean_text:
                raise HTTPException(status_code=400, detail="No text provided for speech synthesis")
            
            # Generate speech using OpenAI TTS
            response = self.openai_client.audio.speech.create(
                model="tts-1",  # Faster model (2x speed, minimal quality difference)
                voice=voice,
                input=clean_text,
                response_format="mp3",
                speed=1.0
            )
            
            return response.content
            
        except Exception as e:
            error_message = str(e)
            
            # Handle rate limiting specifically
            if "429" in error_message or "rate limit" in error_message.lower():
                raise HTTPException(
                    status_code=429, 
                    detail="Speech synthesis rate limit exceeded. Please try again in a few moments."
                )
            
            # Handle other OpenAI API errors
            if "401" in error_message or "unauthorized" in error_message.lower():
                raise HTTPException(
                    status_code=503, 
                    detail="Speech synthesis service temporarily unavailable."
                )
                
            # Generic error fallback
            raise HTTPException(status_code=500, detail=f"Speech generation failed: {str(e)}")

@router.head("/speech/transcribe")
async def transcribe_speech_head():
    """Handle HEAD requests for speech transcription endpoint"""
    return Response(status_code=200)

@router.post("/speech/transcribe")
async def transcribe_speech(
    audio: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Transcribe audio to text using OpenAI Whisper"""
    try:
        service = SpeechService()
        
        # Validate file type
        if not audio.content_type or not audio.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="Invalid audio file format")
        
        transcript = await service.transcribe_audio(audio)
        
        return create_success_response(
            data={"transcript": transcript},
            message="Audio transcribed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.head("/speech/synthesize")
async def synthesize_speech_head():
    """Handle HEAD requests for speech synthesis endpoint"""
    return Response(status_code=200)

@router.post("/speech/synthesize")
async def synthesize_speech(
    text: str = Form(...),
    voice: str = Form(default="alloy"),
    restaurant_slug: Optional[str] = Form(default=None),
    db: Session = Depends(get_db)
):
    """Generate speech from text using OpenAI TTS"""
    try:
        service = SpeechService()
        
        # Validate voice option
        valid_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        if voice not in valid_voices:
            voice = "alloy"  # Default fallback
        
        # Generate speech
        audio_content = await service.generate_speech(text, voice)
        
        # Return audio as streaming response
        return StreamingResponse(
            io.BytesIO(audio_content),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=speech.mp3"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.options("/speech/voices")
async def options_available_voices():
    """Handle preflight CORS requests for voices endpoint"""
    return {}

@router.get("/speech/voices")
async def get_available_voices():
    """Get list of available TTS voices"""
    try:
        voices = [
            {
                "id": "alloy",
                "name": "Alloy",
                "description": "Neutral and balanced, good for both male and female characters",
                "gender": "neutral",
                "recommended_for": "general_purpose"
            },
            {
                "id": "echo", 
                "name": "Echo",
                "description": "Male voice, clear and professional",
                "gender": "male",
                "recommended_for": "professional_announcements"
            },
            {
                "id": "fable",
                "name": "Fable", 
                "description": "Male voice, warm and storytelling",
                "gender": "male",
                "recommended_for": "friendly_conversations"
            },
            {
                "id": "onyx",
                "name": "Onyx",
                "description": "Male voice, deep and authoritative", 
                "gender": "male",
                "recommended_for": "formal_interactions"
            },
            {
                "id": "nova",
                "name": "Nova",
                "description": "Female voice, young and energetic",
                "gender": "female", 
                "recommended_for": "bakery_assistant"
            },
            {
                "id": "shimmer",
                "name": "Shimmer",
                "description": "Female voice, soft and gentle",
                "gender": "female",
                "recommended_for": "customer_service"
            }
        ]
        
        return create_success_response(
            data={"voices": voices},
            message="Available voices retrieved successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/speech/config")
async def get_speech_config():
    """Get speech service configuration including text-only mode status"""
    try:
        service = SpeechService()
        
        return create_success_response(
            data={
                "text_only_mode": service.text_only_mode,
                "api_available": service.api_key_available
            },
            message="Speech configuration retrieved successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")