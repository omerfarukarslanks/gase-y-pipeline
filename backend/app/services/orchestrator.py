"""
Master pipeline orchestrator.

Coordinates the entire video generation flow:
Prompt → Analyze → Script → Translate → TTS → Video Compose → Thumbnail → SEO → Publish
"""

import logging

from app.providers.ai.factory import AIProviderFactory
from app.providers.tts.factory import TTSProviderFactory

logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    def __init__(self, ai_provider: str = "openai", tts_provider: str = "elevenlabs"):
        self.ai = AIProviderFactory.create(ai_provider)
        self.tts = TTSProviderFactory.create(tts_provider)

    async def analyze_and_generate_script(self, prompt: str) -> dict:
        """Step 1-2: Analyze prompt and generate script."""
        logger.info("Analyzing prompt...")
        analysis = await self.ai.analyze_prompt(prompt)

        logger.info("Generating script...")
        scenes = await self.ai.generate_script(analysis)

        return {
            "analysis": analysis,
            "scenes": scenes,
        }

    async def translate_script(
        self, scenes: list[dict], target_language: str
    ) -> list[dict]:
        """Step 3: Translate script scenes to target language."""
        translated_scenes = []
        for scene in scenes:
            translated = scene.copy()
            if scene.get("narration"):
                translated["narration"] = await self.ai.translate(
                    scene["narration"], target_language
                )
            if scene.get("overlay_text"):
                translated["overlay_text"] = await self.ai.translate(
                    scene["overlay_text"], target_language
                )
            translated_scenes.append(translated)
        return translated_scenes

    async def generate_narration(
        self, scenes: list[dict], voice_id: str | None = None, language: str = "en"
    ) -> list[bytes]:
        """Step 4: Generate TTS audio for each scene."""
        audio_clips = []
        for scene in scenes:
            narration_text = scene.get("narration", "")
            if narration_text:
                audio = await self.tts.generate_speech(
                    narration_text, voice_id=voice_id, language=language
                )
                audio_clips.append(audio)
            else:
                audio_clips.append(b"")
        return audio_clips

    async def translate_metadata(
        self, title: str, description: str, target_language: str
    ) -> dict:
        """Translate video title and description for publishing."""
        translated_title = await self.ai.translate(title, target_language)
        translated_description = await self.ai.translate(description, target_language)
        return {
            "title": translated_title,
            "description": translated_description,
        }
