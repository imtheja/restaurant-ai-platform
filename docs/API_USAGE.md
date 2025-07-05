# API Usage Documentation

## Overview
The Restaurant AI Platform uses OpenAI APIs for speech transcription, synthesis, and chat functionality.

## APIs Used

### 1. Speech Transcription (Speech → Text)
- **API**: OpenAI Whisper API
- **Model**: `whisper-1`
- **Endpoint**: `https://api.openai.com/v1/audio/transcriptions`
- **Cost**: ~$0.006 per minute of audio
- **Usage**: Converts customer voice input to text

### 2. Speech Synthesis (Text → Speech)
- **API**: OpenAI Text-to-Speech (TTS) API
- **Model**: `tts-1-hd` (High Definition)
- **Endpoint**: `https://api.openai.com/v1/audio/speech`
- **Cost**: ~$0.015 per 1K characters
- **Available Voices**: alloy, echo, fable, onyx, nova, shimmer
- **Usage**: Converts AI responses to speech

### 3. Chat Streaming (AI Conversation)
- **API**: OpenAI Chat Completions API
- **Model**: `gpt-4o-mini` (Fast & Cost-Effective)
- **Endpoint**: `https://api.openai.com/v1/chat/completions`
- **Cost**: 
  - Input: ~$0.00015 per 1K tokens
  - Output: ~$0.0006 per 1K tokens
- **Usage**: Generates AI responses with streaming support

## Cost Breakdown

| Feature | API | Model | Approximate Cost |
|---------|-----|-------|-----------------|
| Speech Transcription | OpenAI Whisper | `whisper-1` | $0.006/minute |
| Speech Synthesis | OpenAI TTS | `tts-1-hd` | $0.015/1K chars |
| Chat Streaming | OpenAI Chat | `gpt-4o-mini` | $0.00075/1K tokens |

## Environment Configuration

### Required Environment Variables
```bash
# OpenAI API Key (required for all features)
OPENAI_API_KEY=sk-proj-xxxxx

# Model Selection (optional, defaults shown)
OPENAI_MODEL=gpt-4o-mini
```

## Implementation Details

### Speech Service (`backend/ai-service/routers/speech.py`)
- Handles both transcription and synthesis
- Fallback to mock responses if API key not configured
- Supports multiple voice options for TTS

### AI Service (`backend/ai-service/services/ai_service.py`)
- Uses streaming for real-time responses
- Redis caching for common menu questions
- Context-aware conversations with history

## Performance Optimizations

1. **Model Selection**: Using `gpt-4o-mini` for 10x faster responses vs GPT-4
2. **Redis Caching**: Common menu questions cached for instant responses
3. **Streaming**: Real-time text display while response generates
4. **Concurrent Processing**: Speech synthesis can start before full text completion

## Rate Limits

- **Whisper API**: 50 requests/minute
- **TTS API**: 50 requests/minute
- **Chat API**: 10,000 requests/minute for gpt-4o-mini

## Best Practices

1. Always validate API key availability before making requests
2. Implement proper error handling for rate limits
3. Use streaming for better perceived performance
4. Cache frequently requested data to reduce API calls