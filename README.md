# Voice-Based Meeting Summarizer

Welcome to the Voice-Based Meeting Summarizer! This project is an educational, production-ready system designed to take a long meeting audio file, transcribe it into text, extract key points using an AI language model, and read the summary back to you.

## 🧠 Core Concepts (Beginner Friendly)

If you're new to AI engineering, here's a breakdown of the magic happening behind the scenes:

1. **Speech-to-Text (STT):** We use **OpenAI's Whisper** model. Think of Whisper as a very fast typist who listens to the audio and types out every word.
2. **Chunking:** Audio files can be huge! If you try to send a 2-hour audio file to an AI model all at once, it might crash or run out of memory. We use a library called `pydub` to slice the audio into smaller 10-minute "chunks". We process them one by one, then stitch the text together.
3. **Large Language Models (LLMs):** Once we have the full transcript, it's just a giant wall of text. We send this to **GPT-4o-mini**. We use a technique called "Structured Outputs" (via Pydantic) to force the AI to return data in a strict JSON format (Key Points, Action Items, Decisions, Summary).
4. **Text-to-Speech (TTS):** We take the executive summary text and send it to **ElevenLabs**, which uses highly realistic AI voices to read the text out loud, returning an MP3 file.
5. **FastAPI & Async:** The whole system runs on a web framework called FastAPI. We use `async` (asynchronous) programming, meaning the server doesn't freeze while waiting for OpenAI or ElevenLabs to respond. It can handle other requests in the meantime.

## 📂 Project Structure

- `main.py`: The entry point. It starts the server.
- `core/config.py`: Loads our API keys securely from the `.env` file.
- `models/schemas.py`: Defines the strict data structures (Pydantic models) we expect from the LLM and send back to the user.
- `api/routes.py`: Defines the `/summarize` URL endpoint. This is the "manager" that calls all the services in order.
- `services/`: The actual workers.
  - `audio_processor.py`: Chops up long audio files.
  - `stt_service.py`: Talks to OpenAI Whisper.
  - `summarizer_service.py`: Talks to OpenAI GPT.
  - `tts_service.py`: Talks to ElevenLabs.
- `temp_audio/`: A temporary folder where audio chunks and summaries are saved.

## 🛠️ Setup Instructions

### 1. Prerequisites
- Python 3.10+
- `ffmpeg` installed on your system (Required by `pydub` to manipulate audio).
  - On Ubuntu/Debian: `sudo apt install ffmpeg`
  - On Mac: `brew install ffmpeg`

### 2. Install Dependencies
```bash
# Create a virtual environment
python3 -m venv venv

# Activate it (Linux/Mac)
source venv/bin/activate

# Install the required packages
pip install -r requirements.txt
```

### 3. Environment Variables
Copy the `.env.example` file to a new file called `.env`:
```bash
cp .env.example .env
```
Open `.env` and fill in your API keys:
- `OPENAI_API_KEY`: Get this from [platform.openai.com](https://platform.openai.com)
- `ELEVENLABS_API_KEY`: Get this from [elevenlabs.io](https://elevenlabs.io)

### 4. Run the Server
```bash
uvicorn main:app --reload
```
The server will start at `http://127.0.0.1:8000`.

## 🚀 Example Usage

FastAPI comes with a built-in testing interface called Swagger UI.
1. Open your browser and go to `http://127.0.0.1:8000/docs`
2. Click on the `/summarize` endpoint.
3. Click **"Try it out"**.
4. Upload an audio file (mp3, m4a, or wav).
5. Click **"Execute"**.

*Wait for a few moments as the AI processes the audio...*

**The Response:**
You will receive a beautiful JSON response containing:
```json
{
  "key_points": ["Point 1", "Point 2"],
  "action_items": ["Alice needs to review the PR"],
  "decisions_made": ["We will use FastAPI for the backend"],
  "executive_summary": "The team discussed the new backend architecture...",
  "audio_summary_url": "/download/1234_summary.mp3"
}
```
You can then visit `http://127.0.0.1:8000/download/1234_summary.mp3` to listen to the AI-generated voice summary!

## 🔮 Advanced Extensibility

This system is modular. To add real-time streaming transcription in the future, you would simply create a new endpoint in `api/routes.py` that accepts WebSockets, and create a new service `services/streaming_stt_service.py` using Deepgram's streaming API, keeping the rest of the architecture intact!
