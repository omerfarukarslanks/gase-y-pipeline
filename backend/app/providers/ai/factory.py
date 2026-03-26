from app.providers.ai.claude_provider import ClaudeProvider
from app.providers.ai.openai_provider import OpenAIProvider
from app.providers.base import BaseAIProvider


class AIProviderFactory:
    _providers: dict[str, type[BaseAIProvider]] = {
        "openai": OpenAIProvider,
        "claude": ClaudeProvider,
    }

    @classmethod
    def create(cls, provider_name: str) -> BaseAIProvider:
        provider_class = cls._providers.get(provider_name)
        if not provider_class:
            raise ValueError(
                f"Unknown AI provider: {provider_name}. Available: {list(cls._providers.keys())}"
            )
        return provider_class()

    @classmethod
    def available_providers(cls) -> list[str]:
        return list(cls._providers.keys())
