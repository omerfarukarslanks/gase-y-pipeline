from elevenlabs import AsyncElevenLabs

from app.config import settings
from app.providers.base import BaseTTSProvider


class ElevenLabsTTSProvider(BaseTTSProvider):
    def __init__(self):
        self.client = AsyncElevenLabs(api_key=settings.ELEVENLABS_API_KEY)

    async def generate_speech(
        self, text: str, voice_id: str | None = None, language: str = "en"
    ) -> bytes:
        voice = voice_id or "21m00Tcm4TlvDq8ikWAM"  # Default: Rachel
        audio_generator = await self.client.text_to_speech.convert(
            voice_id=voice,
            text=text,
            model_id="eleven_multilingual_v2",
        )
        # Collect audio bytes from the async generator
        audio_bytes = b""
        async for chunk in audio_generator:
            audio_bytes += chunk
        return audio_bytes

    async def list_voices(self, language: str | None = None) -> list[dict]:
        response = await self.client.voices.get_all()
        voices = [
            {"id": v.voice_id, "name": v.name, "labels": v.labels}
            for v in response.voices
        ]
        return voices
