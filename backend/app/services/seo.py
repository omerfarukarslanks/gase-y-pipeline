"""Hashtag & SEO optimization service."""

from app.providers.ai.factory import AIProviderFactory


class SEOService:
    def __init__(self, ai_provider: str = "openai"):
        self.ai = AIProviderFactory.create(ai_provider)

    async def generate_hashtags(
        self, content: str, platform: str, language: str = "en"
    ) -> list[str]:
        """Generate platform-optimized hashtags."""
        prompt = (
            f"Generate 10-15 relevant hashtags for {platform} about the following content. "
            f"Language: {language}. Return only hashtags, one per line, without #.\n\n{content}"
        )
        result = await self.ai.translate(prompt, language)  # Reusing translate as generic text gen
        return [tag.strip().lstrip("#") for tag in result.strip().split("\n") if tag.strip()]

    async def optimize_description(
        self, content: str, platform: str, language: str = "en"
    ) -> str:
        """Generate platform-optimized description."""
        max_lengths = {
            "youtube": 5000,
            "instagram": 2200,
            "twitter": 280,
            "tiktok": 2200,
            "reddit": 300,
        }
        max_len = max_lengths.get(platform, 2000)
        prompt = (
            f"Write a {platform} description (max {max_len} chars) for this video content. "
            f"Language: {language}. Be engaging and include a call-to-action.\n\n{content}"
        )
        return await self.ai.translate(prompt, language)
