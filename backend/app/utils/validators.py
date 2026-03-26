"""Input validators."""

SUPPORTED_LANGUAGES = {
    "en": "English",
    "tr": "Turkish",
    "de": "German",
    "fr": "French",
    "es": "Spanish",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese",
    "ar": "Arabic",
    "pt": "Portuguese",
    "ru": "Russian",
    "it": "Italian",
    "nl": "Dutch",
    "hi": "Hindi",
}

SUPPORTED_PLATFORMS = ["youtube", "instagram", "twitter", "reddit", "tiktok"]

SUPPORTED_ASPECT_RATIOS = ["16:9", "9:16", "1:1"]

SUPPORTED_RESOLUTIONS = ["1080p", "720p"]


def validate_language(language: str) -> bool:
    return language in SUPPORTED_LANGUAGES


def validate_platform(platform: str) -> bool:
    return platform in SUPPORTED_PLATFORMS


def validate_aspect_ratio(ratio: str) -> bool:
    return ratio in SUPPORTED_ASPECT_RATIOS
