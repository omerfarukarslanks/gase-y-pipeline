from abc import ABC, abstractmethod


class BaseAIProvider(ABC):
    """Abstract base class for AI text generation providers."""

    @abstractmethod
    async def analyze_prompt(self, prompt: str) -> dict:
        """Analyze a user prompt and extract intent, mood, structure suggestions."""
        ...

    @abstractmethod
    async def generate_script(self, analyzed_content: dict) -> list[dict]:
        """Generate video script from analyzed content.
        Returns list of scenes: [{scene, narration, overlay_text, duration}]
        """
        ...

    @abstractmethod
    async def translate(self, text: str, target_language: str) -> str:
        """Translate text to the target language."""
        ...


class BaseTTSProvider(ABC):
    """Abstract base class for text-to-speech providers."""

    @abstractmethod
    async def generate_speech(
        self, text: str, voice_id: str | None = None, language: str = "en"
    ) -> bytes:
        """Generate speech audio from text. Returns audio bytes."""
        ...

    @abstractmethod
    async def list_voices(self, language: str | None = None) -> list[dict]:
        """List available voices, optionally filtered by language."""
        ...


class BaseImageProvider(ABC):
    """Abstract base class for image generation providers."""

    @abstractmethod
    async def generate_image(self, prompt: str, width: int = 1280, height: int = 720) -> bytes:
        """Generate an image from a text prompt. Returns image bytes."""
        ...


class BasePlatformPublisher(ABC):
    """Abstract base class for social media platform publishers."""

    @abstractmethod
    async def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: list[str] | None = None,
        **kwargs,
    ) -> dict:
        """Upload video to the platform. Returns platform-specific response with post ID and URL."""
        ...

    @abstractmethod
    async def get_oauth_url(self, state: str) -> str:
        """Generate OAuth authorization URL for this platform."""
        ...

    @abstractmethod
    async def exchange_code(self, code: str) -> dict:
        """Exchange OAuth authorization code for access/refresh tokens."""
        ...
