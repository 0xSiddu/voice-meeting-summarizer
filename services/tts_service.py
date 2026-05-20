import os
import httpx
from core.config import settings

async def generate_audio_summary(text: str, output_path: str) -> str:
    """
    Takes the executive summary text and sends it to ElevenLabs to be spoken
    by an AI voice. Saves the resulting audio to output_path.
    
    Args:
        text (str): The text to be spoken.
        output_path (str): The file path where the mp3 should be saved.
        
    Returns:
        str: The path to the saved audio file.
    """
    if not settings.elevenlabs_api_key:
        print("No ElevenLabs API key found, skipping TTS generation.")
        return ""
        
    # We'll use a popular default voice (Rachel)
    voice_id = "21m00Tcm4TlvDq8ikWAM" 
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": settings.elevenlabs_api_key
    }
    
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    
    try:
        # Use httpx for asynchronous HTTP requests
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers, timeout=30.0)
            
            if response.status_code != 200:
                print(f"ElevenLabs Error: {response.text}")
                return ""
                
            # Save the binary audio data to a file
            with open(output_path, "wb") as f:
                f.write(response.content)
                
            return output_path
            
    except Exception as e:
        print(f"Failed to generate TTS: {str(e)}")
        return ""
