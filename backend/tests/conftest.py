import pytest


@pytest.fixture
def sample_prompt():
    return "Create a 30-second educational video about climate change"


@pytest.fixture
def sample_scenes():
    return [
        {
            "scene_number": 1,
            "narration": "Climate change is one of the greatest challenges of our time.",
            "overlay_text": "Climate Change",
            "visual_description": "Earth from space",
            "duration_sec": 5,
        },
        {
            "scene_number": 2,
            "narration": "Rising temperatures affect every corner of the planet.",
            "overlay_text": "Rising Temperatures",
            "visual_description": "Temperature graph",
            "duration_sec": 5,
        },
    ]
