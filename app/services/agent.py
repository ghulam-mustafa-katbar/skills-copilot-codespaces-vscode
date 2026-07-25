"""Top-level orchestrator service."""

from pathlib import Path

from loguru import logger

from app.ai.providers import OllamaProvider
from app.config.settings import Settings
from app.core.logging import configure_logging
from app.database.base import Base, SessionLocal, engine
from app.scheduler.upload_scheduler import UploadScheduler
from app.seo.generator import SEOGenerator
from app.services.state import RuntimeState
from app.services.upload_manager import UploadManager
from app.watcher.folder_watcher import FolderWatcher
from app.youtube.client import YouTubeClient


class YouTubeAutomationAgent:
    """Coordinates watcher, scheduler and upload manager."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        configure_logging(settings.log_level)
        settings.ensure_directories(Path.cwd())
        Base.metadata.create_all(bind=engine)

        self.state = RuntimeState(running=False)
        self._session = SessionLocal()
        provider = OllamaProvider(settings.ollama_url, settings.ollama_model)
        seo_generator = SEOGenerator(settings, provider)
        youtube_client = YouTubeClient(settings)
        self.upload_manager = UploadManager(settings, self._session, seo_generator, youtube_client)

        self.scheduler = UploadScheduler()
        self.watcher = FolderWatcher(settings.upload_folder, callback=lambda _: self.scan_and_queue())

    def start(self) -> None:
        """Start automation components."""

        self.scan_and_queue()
        self.scheduler.start()
        self.scheduler.schedule_interval(self.scan_and_upload, self.settings.upload_interval)
        self.watcher.start()
        self.state.running = True
        logger.info("YouTube Automation Agent started")

    def stop(self) -> None:
        """Stop automation components."""

        self.watcher.stop()
        self.scheduler.stop()
        self._session.close()
        self.state.running = False
        logger.info("YouTube Automation Agent stopped")

    def scan_and_queue(self) -> int:
        """Discover and queue new videos."""

        count = self.upload_manager.queue_new_videos()
        self.state.last_scan_count = count
        return count

    def upload_now(self) -> int:
        """Process queued uploads immediately."""

        count = self.upload_manager.process_queue()
        self.state.last_processed_count = count
        return count

    def scan_and_upload(self) -> None:
        """Periodic routine for scheduler."""

        self.scan_and_queue()
        self.upload_now()
