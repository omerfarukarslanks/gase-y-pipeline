from app.providers.base import BaseTTSProvider
from app.providers.tts.elevenlabs import ElevenLabsTTSProvider
from app.providers.tts.google_tts import GoogleTTSProvider


class TTSProviderFactory:
    _providers: dict[str, type[BaseTTSProvider]] = {
        "elevenlabs": ElevenLabsTTSProvider,
        "google_tts": GoogleTTSProvider,
    }

    @classmethod
    def create(cls, provider_name: str) -> BaseTTSProvider:
        provider_class = cls._providers.get(provider_name)
        if not provider_class:
            raise ValueError(
                f"Unknown TTS provider: {provider_name}. Available: {list(cls._providers.keys())}"
            )
        return provider_class()

    @classmethod
    def available_providers(cls) -> list[str]:
        return list(cls._providers.keys())
