import httpx

from app.config import settings
from app.providers.base import BaseImageProvider


class StabilityProvider(BaseImageProvider):
    BASE_URL = "https://api.stability.ai/v2beta"

    def __init__(self):
        self.api_key = settings.STABILITY_API_KEY

    async def generate_image(self, prompt: str, width: int = 1280, height: int = 720) -> bytes:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/stable-image/generate/sd3",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Accept": "image/*",
                },
                files={"none": ""},
                data={
                    "prompt": prompt,
                    "width": width,
                    "height": height,
                    "output_format": "png",
                },
            )
            response.raise_for_status()
            return response.content
