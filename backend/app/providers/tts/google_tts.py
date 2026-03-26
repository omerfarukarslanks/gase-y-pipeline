from app.providers.base import BaseTTSProvider


class GoogleTTSProvider(BaseTTSProvider):
    def __init__(self):
        # google.cloud.texttospeech requires credentials set up
        from google.cloud import texttospeech_v1 as texttospeech

        self.client = texttospeech.TextToSpeechAsyncClient()
        self.texttospeech = texttospeech

    async def generate_speech(
        self, text: str, voice_id: str | None = None, language: str = "en"
    ) -> bytes:
        language_code = self._get_language_code(language)

        synthesis_input = self.texttospeech.SynthesisInput(text=text)
        voice = self.texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_id,
        )
        audio_config = self.texttospeech.AudioConfig(
            audio_encoding=self.texttospeech.AudioEncoding.MP3
        )

        response = await self.client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        return response.audio_content

    async def list_voices(self, language: str | None = None) -> list[dict]:
        language_code = self._get_language_code(language) if language else None
        response = await self.client.list_voices(language_code=language_code)
        return [
            {"id": v.name, "name": v.name, "language_codes": list(v.language_codes)}
            for v in response.voices
        ]

    @staticmethod
    def _get_language_code(language: str) -> str:
        mapping = {
            "en": "en-US",
            "tr": "tr-TR",
            "de": "de-DE",
            "fr": "fr-FR",
            "es": "es-ES",
            "ja": "ja-JP",
            "ko": "ko-KR",
            "zh": "zh-CN",
            "ar": "ar-XA",
            "pt": "pt-BR",
        }
        return mapping.get(language, f"{language}-{language.upper()}")
