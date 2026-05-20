import os
import math
from pydub import AudioSegment
from core.config import settings

def chunk_audio(file_path: str, output_dir: str) -> list[str]:
    """
    Takes a large audio file and splits it into smaller chunks.
    This is necessary because STT APIs often have file size or length limits.
    
    Args:
        file_path (str): The path to the original large audio file.
        output_dir (str): The folder where the smaller chunks will be saved.
        
    Returns:
        list[str]: A list of file paths pointing to the newly created chunks.
    """
    # Load the audio file using pydub. 
    # Pydub reads the file into memory so we can manipulate it.
    try:
        audio = AudioSegment.from_file(file_path)
    except Exception as e:
        raise Exception(f"Failed to load audio file: {str(e)}")

    audio_length_ms = len(audio)
    chunk_paths = []
    
    # If the audio is shorter than our threshold, we don't need to chunk it.
    if audio_length_ms <= settings.chunk_threshold_ms:
        return [file_path]
    
    # Calculate how many chunks we need
    num_chunks = math.ceil(audio_length_ms / settings.chunk_threshold_ms)
    print(f"Audio is long ({audio_length_ms}ms). Splitting into {num_chunks} chunks.")
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    for i in range(num_chunks):
        start_time = i * settings.chunk_threshold_ms
        end_time = min((i + 1) * settings.chunk_threshold_ms, audio_length_ms)
        
        # Slicing the audio in pydub is as easy as slicing a Python list
        chunk = audio[start_time:end_time]
        
        # Create a unique filename for the chunk
        chunk_filename = f"chunk_{i}.mp3"
        chunk_path = os.path.join(output_dir, chunk_filename)
        
        # Export the chunk to the file system
        chunk.export(chunk_path, format="mp3")
        chunk_paths.append(chunk_path)
        print(f"Exported {chunk_filename}")
        
    return chunk_paths
