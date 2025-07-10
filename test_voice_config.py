#!/usr/bin/env python3
"""
Test script to check current voice configuration and generate test audio samples
"""

import os
import sys
import requests
import json
from datetime import datetime

# Add the backend directory to Python path
sys.path.append('/Users/tejasmachine/Research/restaurant-ai-platform/backend')

def test_voice_api():
    """Test the voice API endpoints"""
    ai_service_url = "http://localhost:8003"
    
    print("=" * 60)
    print("VOICE CONFIGURATION INVESTIGATION")
    print("=" * 60)
    print(f"Timestamp: {datetime.now()}")
    print()
    
    # Test 1: Get available voices
    print("1. Testing available voices endpoint...")
    try:
        response = requests.get(f"{ai_service_url}/api/v1/speech/voices")
        if response.status_code == 200:
            voices_data = response.json()
            print("✅ Successfully retrieved available voices:")
            print(json.dumps(voices_data, indent=2))
            print()
            
            # Extract voice information
            if voices_data.get('success') and voices_data.get('data', {}).get('voices'):
                voices = voices_data['data']['voices']
                nova_voice = next((v for v in voices if v['id'] == 'nova'), None)
                if nova_voice:
                    print("🔍 Nova voice configuration:")
                    print(f"   ID: {nova_voice['id']}")
                    print(f"   Name: {nova_voice['name']}")
                    print(f"   Description: {nova_voice['description']}")
                    print(f"   Gender: {nova_voice['gender']}")
                    print(f"   Recommended for: {nova_voice['recommended_for']}")
                    print()
                else:
                    print("❌ Nova voice not found in available voices!")
                    print()
        else:
            print(f"❌ Failed to get voices: {response.status_code}")
            print(f"Response: {response.text}")
            print()
    except Exception as e:
        print(f"❌ Error testing voices endpoint: {e}")
        print()
    
    # Test 2: Generate speech samples with different voices
    test_text = "Hello! I'm Baker Betty from The Cookie Jar. Welcome to our bakery!"
    voices_to_test = ['nova', 'alloy', 'echo', 'fable', 'onyx', 'shimmer']
    
    print("2. Testing speech synthesis with different voices...")
    for voice in voices_to_test:
        print(f"   Testing voice: {voice}")
        try:
            data = {
                'text': test_text,
                'voice': voice,
                'restaurant_slug': 'the-cookie-jar'
            }
            response = requests.post(f"{ai_service_url}/api/v1/speech/synthesize", data=data)
            
            if response.status_code == 200:
                # Save audio file
                output_file = f"/Users/tejasmachine/Research/restaurant-ai-platform/test_voice_{voice}.mp3"
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                
                file_size = len(response.content)
                print(f"   ✅ {voice}: Generated {file_size} bytes -> {output_file}")
                
                # Check if it's a real audio file or just a placeholder
                if file_size < 100:
                    print(f"   ⚠️  {voice}: File size too small, likely a placeholder/fallback")
                else:
                    print(f"   ✅ {voice}: Good file size, likely real audio")
            else:
                print(f"   ❌ {voice}: Failed - {response.status_code}")
                print(f"      Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"   ❌ {voice}: Error - {e}")
        
        print()
    
    # Test 3: Check environment variables
    print("3. Checking environment variables...")
    env_vars = [
        'OPENAI_API_KEY',
        'OPENAI_MODEL',
        'AI_PROVIDER',
        'GROQ_API_KEY',
        'GROK_API_KEY'
    ]
    
    for var in env_vars:
        value = os.getenv(var, 'Not set')
        if 'API_KEY' in var and value != 'Not set':
            # Mask API keys for security
            if len(value) > 10:
                masked_value = value[:4] + '***' + value[-4:]
            else:
                masked_value = '***'
            print(f"   {var}: {masked_value}")
        else:
            print(f"   {var}: {value}")
    print()
    
    # Test 4: Check if OpenAI client is working
    print("4. Testing OpenAI API connectivity...")
    try:
        # Import and test OpenAI client
        import openai
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key.startswith("your_") or api_key == "sk-fake-key-for-development-only":
            print("   ❌ OpenAI API key not properly configured")
            print("   🔧 This is why you're getting fallback responses instead of Nova voice")
        else:
            client = openai.OpenAI(api_key=api_key)
            print("   ✅ OpenAI client initialized successfully")
            
            # Test a simple TTS call directly
            try:
                response = client.audio.speech.create(
                    model="tts-1",
                    voice="nova",
                    input="This is a test of the Nova voice.",
                    response_format="mp3"
                )
                
                # Save the test file
                test_file = "/Users/tejasmachine/Research/restaurant-ai-platform/direct_nova_test.mp3"
                with open(test_file, 'wb') as f:
                    f.write(response.content)
                
                print(f"   ✅ Direct OpenAI TTS test successful -> {test_file}")
                print(f"   📊 Audio file size: {len(response.content)} bytes")
                
            except Exception as e:
                print(f"   ❌ Direct OpenAI TTS test failed: {e}")
                
    except ImportError:
        print("   ❌ OpenAI library not available")
    except Exception as e:
        print(f"   ❌ Error testing OpenAI connectivity: {e}")
    
    print()
    print("=" * 60)
    print("INVESTIGATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_voice_api()