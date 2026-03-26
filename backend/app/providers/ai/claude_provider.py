import json

from anthropic import AsyncAnthropic

from app.config import settings
from app.providers.base import BaseAIProvider


class ClaudeProvider(BaseAIProvider):
    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-20250514"

    async def analyze_prompt(self, prompt: str) -> dict:
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=(
                "You are a video content analyzer. Analyze the user's prompt and return a JSON object with: "
                "intent, mood, target_audience, suggested_duration_sec, scene_count, style, content_type. "
                "Return valid JSON only, no markdown."
            ),
            messages=[{"role": "user", "content": prompt}],
        )
        return json.loads(response.content[0].text)

    async def generate_script(self, analyzed_content: dict) -> list[dict]:
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=(
                "You are a video script writer. Based on the analysis, generate a video script as a JSON object "
                "with a 'scenes' key containing an array. Each element: "
                "{scene_number, narration, overlay_text, visual_description, duration_sec}. "
                "Return valid JSON only."
            ),
            messages=[{"role": "user", "content": json.dumps(analyzed_content)}],
        )
        result = json.loads(response.content[0].text)
        return result.get("scenes", result.get("script", []))

    async def translate(self, text: str, target_language: str) -> str:
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=f"Translate the following text to {target_language}. Return only the translation.",
            messages=[{"role": "user", "content": text}],
        )
        return response.content[0].text
