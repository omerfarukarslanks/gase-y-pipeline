import json

from openai import AsyncOpenAI

from app.config import settings
from app.providers.base import BaseAIProvider


class OpenAIProvider(BaseAIProvider):
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o"

    async def analyze_prompt(self, prompt: str) -> dict:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a video content analyzer. Analyze the user's prompt and return a JSON object with: "
                        "intent (what the video should convey), mood (emotional tone), "
                        "target_audience, suggested_duration_sec, scene_count, style (modern/minimal/energetic/calm), "
                        "and content_type (educational/promotional/entertainment/motivational)."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)

    async def generate_script(self, analyzed_content: dict) -> list[dict]:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a video script writer. Based on the analysis, generate a video script as a JSON array. "
                        "Each element: {scene_number, narration, overlay_text, visual_description, duration_sec}. "
                        "Keep narration concise and engaging. Return JSON array only."
                    ),
                },
                {"role": "user", "content": json.dumps(analyzed_content)},
            ],
            response_format={"type": "json_object"},
        )
        result = json.loads(response.choices[0].message.content)
        return result.get("scenes", result.get("script", []))

    async def translate(self, text: str, target_language: str) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": f"Translate the following text to {target_language}. Return only the translation.",
                },
                {"role": "user", "content": text},
            ],
        )
        return response.choices[0].message.content
