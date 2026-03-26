from app.providers.base import BaseImageProvider
from app.providers.image.dalle import DallEProvider
from app.providers.image.stability import StabilityProvider


class ImageProviderFactory:
    _providers: dict[str, type[BaseImageProvider]] = {
        "dalle": DallEProvider,
        "stability": StabilityProvider,
    }

    @classmethod
    def create(cls, provider_name: str) -> BaseImageProvider:
        provider_class = cls._providers.get(provider_name)
        if not provider_class:
            raise ValueError(
                f"Unknown image provider: {provider_name}. Available: {list(cls._providers.keys())}"
            )
        return provider_class()

    @classmethod
    def available_providers(cls) -> list[str]:
        return list(cls._providers.keys())
