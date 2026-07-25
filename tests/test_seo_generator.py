from pathlib import Path

from app.config.settings import Settings
from app.seo.generator import SEOGenerator


class BrokenProvider:
    def generate(self, prompt: str):  # noqa: ANN201
        return None


def test_seo_generator_fallback_works() -> None:
    settings = Settings()
    generator = SEOGenerator(settings, BrokenProvider())

    metadata = generator.generate(Path("my_test_video.mp4"))

    assert "My Test Video" in metadata.title
    assert "#shorts" in metadata.description
    assert metadata.visibility == settings.youtube_default_visibility
