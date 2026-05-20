import os
import uuid
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, UploadFile, File, HTTPException
# pyrefly: ignore [missing-import]
from fastapi.responses import FileResponse
# pyrefly: ignore [missing-import]
from fastapi.concurrency import run_in_threadpool
from models.schemas import SummaryResponse
from services.audio_processor import chunk_audio
from services.stt_service import transcribe_meeting
from services.summarizer_service import summarize_transcript
from services.tts_service import generate_audio_summary

router = APIRouter()

# We define a temporary directory for our audio processing
TEMP_DIR = "temp_audio"
os.makedirs(TEMP_DIR, exist_ok=True)

@router.post("/summarize", response_model=SummaryResponse)
async def summarize_meeting(file: UploadFile = File(...)):
    """
    The main endpoint for the Meeting Summarizer.
    Takes an audio file, transcribes it, summarizes it, and generates an audio summary.
    """
    
    # 1. Save the uploaded file to disk temporarily
    file_id = str(uuid.uuid4())
    original_file_path = os.path.join(TEMP_DIR, f"{file_id}_{file.filename}")
    
    with open(original_file_path, "wb") as f:
        content = await file.read()
        f.write(content)
        
    try:
        # 2. Chunk the audio if it's too long (Runs in a separate thread so we don't block the server)
        chunk_dir = os.path.join(TEMP_DIR, f"{file_id}_chunks")
        chunk_paths = await run_in_threadpool(chunk_audio, original_file_path, chunk_dir)
        
        # 3. Transcribe the audio chunks
        transcript = await transcribe_meeting(chunk_paths)
        if not transcript:
            raise HTTPException(status_code=500, detail="Failed to transcribe audio.")
            
        # 4. Summarize the transcript using the LLM
        summary_obj = await summarize_transcript(transcript)
        
        # 5. Generate Text-to-Speech from the executive summary
        tts_output_path = os.path.join(TEMP_DIR, f"{file_id}_summary.mp3")
        audio_url = await generate_audio_summary(summary_obj.executive_summary, tts_output_path)
        
        # If TTS was successful, create a downloadable URL path
        # Assuming the FastAPI app will mount the TEMP_DIR as a static directory
        final_audio_url = f"/download/{file_id}_summary.mp3" if audio_url else ""
        
        # 6. Return the structured response
        return SummaryResponse(
            key_points=summary_obj.key_points,
            action_items=summary_obj.action_items,
            decisions_made=summary_obj.decisions_made,
            executive_summary=summary_obj.executive_summary,
            audio_summary_url=final_audio_url
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{filename}")
async def download_audio(filename: str):
    """
    Endpoint to download the generated audio summary.
    """
    file_path = os.path.join(TEMP_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/mpeg", filename=filename)
    raise HTTPException(status_code=404, detail="File not found")
