import httpx
from openai import AsyncOpenAI

from app.config import settings
from app.providers.base import BaseImageProvider


class DallEProvider(BaseImageProvider):
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate_image(self, prompt: str, width: int = 1280, height: int = 720) -> bytes:
        size = self._get_closest_size(width, height)
        response = await self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        async with httpx.AsyncClient() as client:
            img_response = await client.get(image_url)
            return img_response.content

    @staticmethod
    def _get_closest_size(width: int, height: int) -> str:
        if width == height:
            return "1024x1024"
        elif width > height:
            return "1792x1024"
        else:
            return "1024x1792"
