"""SEO metadata generation service."""

from pathlib import Path

from app.ai.providers import OllamaProvider
from app.config.settings import Settings
from app.metadata.schemas import VideoMetadata


class SEOGenerator:
    """Produces SEO-ready metadata for YouTube Shorts."""

    def __init__(self, settings: Settings, provider: OllamaProvider) -> None:
        self.settings = settings
        self.provider = provider

    def generate(self, video_path: Path) -> VideoMetadata:
        """Generate metadata using Ollama, with deterministic fallback."""

        stem = video_path.stem.replace("_", " ").replace("-", " ").strip()
        fallback = VideoMetadata(
            title=f"{stem.title()} | Quick Shorts Insight"[:100],
            description=(
                f"Watch this short on {stem}.\n"
                "Subscribe for more practical insights and quick tutorials.\n"
                "#shorts #automation #ai"
            ),
            tags=["shorts", "ai", "automation", stem.lower()],
            hashtags=["#shorts", "#ai", "#automation"],
            keywords=[stem.lower(), "youtube shorts", "content automation"],
            category="Education",
            language=self.settings.youtube_default_language,
            visibility=self.settings.youtube_default_visibility,
        )

        prompt = (
            "Generate YouTube Shorts metadata as strict JSON with keys: "
            "title, description, tags (array), hashtags (array), keywords (array), "
            "category, language, visibility. "
            f"Video filename: {video_path.name}."
        )
        generated = self.provider.generate(prompt)
        if not generated:
            return fallback

        try:
            return VideoMetadata.model_validate(generated)
        except Exception:
            return fallback
