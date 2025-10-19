# voice_routes.py
import os, time
import httpx
from fastapi import APIRouter, Request, Response, HTTPException
from dotenv import load_dotenv

# load .env (safe if called more than once)
load_dotenv()

router = APIRouter(prefix="/voice", tags=["voice"])

ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID      = os.getenv("ELEVENLABS_VOICE_ID")
MODEL_ID      = os.getenv("ELEVENLABS_TTS_MODEL", "eleven_flash_v2_5")  # good fast default
AGENT_ID      = os.getenv("ELEVENLABS_AGENT_ID")  # optional

if not ELEVEN_API_KEY:
    raise RuntimeError("Missing ELEVENLABS_API_KEY in backend .env")

@router.post("/realtime/token")
async def realtime_token():
    """
    Frontend will call this to start a realtime WebRTC session
    without exposing the real API key in browser code.
    """
    return {
        "provider": "elevenlabs",
        "token": ELEVEN_API_KEY,   # stays server-side; never hardcode in frontend
        "agent_id": AGENT_ID,      # optional convenience for the client
        "issued_at": int(time.time()),
        "expires_in": 55
    }

@router.post("/tts")
async def tts(request: Request):
    """
    Sanity test endpoint:
    POST /voice/tts  with JSON: { "text": "Hello" }
    Returns an MP3 stream from ElevenLabs TTS.
    """
    body = await request.json()
    text = body.get("text", "This is a sanity test for our voice agent.")

    if not VOICE_ID:
        raise HTTPException(500, "Missing ELEVENLABS_VOICE_ID in backend .env")

    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "model_id": MODEL_ID,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.85}
    }
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"

    async with httpx.AsyncClient(timeout=None) as client:
        r = await client.post(url, headers=headers, json=payload)
        if r.status_code >= 400:
            detail = await r.aread()
            raise HTTPException(status_code=r.status_code, detail=detail.decode("utf-8", "ignore"))
        return Response(content=r.iter_bytes(), media_type="audio/mpeg")
