# Voice Meeting Summarizer

Upload a meeting recording. Get back a structured summary and an audio readout of it.

Built with FastAPI, OpenAI Whisper, GPT-4o-mini, and ElevenLabs TTS.

---

## What it does

Most meeting recordings sit in a folder forever because nobody wants to re-listen to a 45-minute call just to find out who was supposed to do what. This tool fixes that.

You throw in an audio file (mp3, wav, m4a — whatever you have), and it:

1. **Transcribes** the entire recording using OpenAI's Whisper
2. **Splits long audio** into chunks automatically so you're not hitting API limits
3. **Summarizes** the transcript through GPT-4o-mini, pulling out the stuff that actually matters
4. **Generates a voice summary** via ElevenLabs so you can listen to the recap on the go

The output is a JSON response with key discussion points, action items, decisions made, and a short executive summary. Plus a downloadable MP3 of the summary read aloud.

---

## Architecture

```
voice_meeting_summarizer/
├── main.py                          # FastAPI entry point
├── core/
│   └── config.py                    # env vars, settings
├── api/
│   └── routes.py                    # POST /summarize, GET /download
├── services/
│   ├── audio_processor.py           # chunking with pydub
│   ├── stt_service.py               # Whisper transcription
│   ├── summarizer_service.py        # GPT structured output
│   └── tts_service.py               # ElevenLabs voice generation
├── models/
│   └── schemas.py                   # Pydantic request/response models
├── temp_audio/                      # runtime temp files (gitignored)
├── requirements.txt
├── .env.example
└── .gitignore
```

The services are intentionally decoupled. Swapping Whisper for Deepgram or GPT for Claude is a single-file change — nothing else needs to know about it.

---

## How the pipeline works

```
Audio File (.mp3/.wav/.m4a)
        │
        ▼
┌─────────────────┐
│ audio_processor  │  ← splits into 10-min chunks if needed
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   stt_service    │  ← Whisper API, chunk by chunk
└────────┬────────┘
         │
         ▼
   Full Transcript
         │
         ▼
┌─────────────────┐
│  summarizer      │  ← GPT-4o-mini w/ structured outputs
└────────┬────────┘
         │
         ▼
   Structured JSON
   (key points, action items, decisions, exec summary)
         │
         ▼
┌─────────────────┐
│   tts_service    │  ← ElevenLabs reads the summary aloud
└────────┬────────┘
         │
         ▼
   Summary MP3 file
```

---

## Prerequisites

- **Python 3.10+**
- **ffmpeg** — needed by pydub for audio processing
  ```bash
  # Ubuntu/Debian
  sudo apt install ffmpeg

  # macOS
  brew install ffmpeg
  ```
- **API Keys** for OpenAI and ElevenLabs (details below)

---

## Setup

```bash
git clone https://github.com/0xSiddu/voice-meeting-summarizer.git
cd voice-meeting-summarizer

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Copy the example env file and fill in your keys:

```bash
cp .env.example .env
```

```
OPENAI_API_KEY=sk-...
ELEVENLABS_API_KEY=...
```

| Variable | Where to get it |
|---|---|
| `OPENAI_API_KEY` | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
| `ELEVENLABS_API_KEY` | [elevenlabs.io/app/settings/api-keys](https://elevenlabs.io/app/settings/api-keys) |

---

## Running

```bash
uvicorn main:app --reload
```

Server starts at `http://localhost:8000`. Hit `/docs` for the interactive Swagger UI.

---

## Usage

### Via Swagger UI (easiest)

1. Go to `http://localhost:8000/docs`
2. Open `POST /summarize`
3. Click "Try it out"
4. Upload your audio file
5. Hit Execute

### Via curl

```bash
curl -X POST http://localhost:8000/summarize \
  -F "file=@meeting_recording.mp3"
```

### Response

```json
{
  "key_points": [
    "Q3 revenue is tracking 12% above forecast",
    "Mobile app redesign pushed to next sprint"
  ],
  "action_items": [
    "Sarah to finalize the vendor contract by Friday",
    "Dev team to scope the auth migration"
  ],
  "decisions_made": [
    "Go with AWS over GCP for the new infra",
    "Hire two more backend engineers in Q4"
  ],
  "executive_summary": "The team reviewed Q3 progress, discussed the infrastructure migration timeline, and agreed on hiring priorities for the remainder of the year.",
  "audio_summary_url": "/download/abc123_summary.mp3"
}
```

The audio file can be downloaded from the URL in the response.

---

## Running on Google Colab

Since Colab doesn't expose localhost, you'll need ngrok to create a public tunnel.

```python
# Cell 1 — Setup
!git clone https://github.com/0xSiddu/voice-meeting-summarizer.git
%cd voice-meeting-summarizer
!pip install -r requirements.txt pyngrok nest-asyncio
!apt-get install -y ffmpeg

# Cell 2 — Write your .env
with open(".env", "w") as f:
    f.write("OPENAI_API_KEY=sk-your-key-here\n")
    f.write("ELEVENLABS_API_KEY=your-key-here\n")

# Cell 3 — Start the server
import nest_asyncio
from pyngrok import ngrok
import uvicorn
from main import app

ngrok.set_auth_token("your-ngrok-token")  # from dashboard.ngrok.com
nest_asyncio.apply()

tunnel = ngrok.connect(8000)
print(f"Public URL: {tunnel.public_url}/docs")
uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## Configuration

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | Required. Used for Whisper + GPT |
| `ELEVENLABS_API_KEY` | — | Optional. Skips TTS if not set |
| `CHUNK_THRESHOLD_MS` | `600000` | Audio chunk size in ms (default 10 min) |

---

## Tech Stack

| Component | Technology |
|---|---|
| Web Framework | FastAPI |
| Speech-to-Text | OpenAI Whisper |
| Summarization | GPT-4o-mini (structured outputs) |
| Text-to-Speech | ElevenLabs |
| Audio Processing | pydub + ffmpeg |
| HTTP Client | httpx (async) |

---

## Extending this

A few things that would be straightforward to add given the current architecture:

- **Speaker diarization** — pipe through pyannote before summarization so the LLM knows who said what
- **Streaming transcription** — add a WebSocket endpoint using Deepgram's real-time API
- **Web UI** — a simple HTML page with a file upload form and a results panel
- **Webhook notifications** — fire a callback when processing finishes for async workflows
- **Storage backend** — swap the local `temp_audio/` dir for S3/GCS in production

---

## License

MIT
