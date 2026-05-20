from openai import AsyncOpenAI
from core.config import settings

# Initialize the OpenAI async client
# We use AsyncOpenAI so that our server doesn't block while waiting for the transcript.
client = AsyncOpenAI(api_key=settings.openai_api_key)

async def transcribe_audio_chunk(file_path: str) -> str:
    """
    Sends a single audio chunk to OpenAI's Whisper model to be transcribed.
    
    Args:
        file_path (str): The path to the audio chunk.
        
    Returns:
        str: The transcribed text.
    """
    try:
        # Open the file in binary read mode as required by the API
        with open(file_path, "rb") as audio_file:
            # Call the Whisper API
            response = await client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file,
                response_format="text" # We just want the raw text back
            )
        return response
    except Exception as e:
        print(f"Error transcribing chunk {file_path}: {e}")
        return ""

async def transcribe_meeting(chunk_paths: list[str]) -> str:
    """
    Takes a list of audio chunk paths, transcribes each one, 
    and concatenates the results into a single full transcript.
    
    Args:
        chunk_paths (list[str]): List of file paths to audio chunks.
        
    Returns:
        str: The full transcript of the meeting.
    """
    full_transcript = []
    
    # Process each chunk sequentially
    # (We could do this concurrently with asyncio.gather, but OpenAI might rate-limit us
    # if we send too many concurrent requests. Sequential is safer for large files).
    for chunk_path in chunk_paths:
        print(f"Transcribing {chunk_path}...")
        text = await transcribe_audio_chunk(chunk_path)
        if text:
            full_transcript.append(text)
            
    # Join all chunk transcripts with a space in between
    return " ".join(full_transcript)
