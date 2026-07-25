"""Workflow service for scanning and uploading videos."""

from datetime import datetime, timedelta
from pathlib import Path
import shutil

from loguru import logger
from sqlalchemy.orm import Session

from app.config.settings import Settings
from app.database.repository import VideoRepository
from app.metadata.schemas import VideoMetadata
from app.seo.generator import SEOGenerator
from app.thumbnails.generator import generate_thumbnail
from app.utils.hashing import calculate_sha256
from app.youtube.client import YouTubeClient


class UploadManager:
    """Coordinates duplicate detection, metadata generation and upload."""

    def __init__(
        self,
        settings: Settings,
        session: Session,
        seo_generator: SEOGenerator,
        youtube_client: YouTubeClient,
    ) -> None:
        self.settings = settings
        self.repository = VideoRepository(session)
        self.seo_generator = seo_generator
        self.youtube_client = youtube_client

    def queue_new_videos(self) -> int:
        """Scan upload folder and queue unseen mp4 files."""

        queued = 0
        upload_dir = Path(self.settings.upload_folder)
        for video_path in sorted(upload_dir.glob("*.mp4")):
            sha256_hash = calculate_sha256(video_path)
            if self.repository.get_by_hash(sha256_hash):
                continue

            metadata = self.seo_generator.generate(video_path)
            scheduled_at = datetime.utcnow() + timedelta(minutes=self.settings.upload_interval)
            self.repository.create(
                file_name=video_path.name,
                file_path=str(video_path),
                sha256_hash=sha256_hash,
                metadata=metadata,
                scheduled_publish_at=scheduled_at,
            )
            queued += 1

        logger.info("Queued {} new videos", queued)
        return queued

    def process_queue(self) -> int:
        """Upload queued videos and update persistent state."""

        processed = 0
        for record in self.repository.list_queued():
            processed += 1
            video_path = Path(record.file_path)
            metadata = VideoMetadata(
                title=record.title,
                description=record.description,
                tags=[tag for tag in record.tags.split(",") if tag],
                hashtags=[tag for tag in record.hashtags.split(",") if tag],
                keywords=[tag for tag in record.keywords.split(",") if tag],
                category=record.category,
                language=record.language,
                visibility=record.visibility,
            )
            try:
                thumbnail_output = Path(self.settings.thumbnail_folder) / f"{video_path.stem}.jpg"
                thumbnail_path = generate_thumbnail(video_path, thumbnail_output)
                video_id = self.youtube_client.upload_video(
                    video_path,
                    metadata,
                    thumbnail_path=thumbnail_path,
                    publish_at=record.scheduled_publish_at,
                )
                self.repository.update_status(record, "uploaded", youtube_video_id=video_id)
                self._move_file(video_path, Path(self.settings.uploaded_folder) / video_path.name)
                logger.info("Uploaded {} as {}", video_path.name, video_id)
            except Exception as exc:
                self.repository.update_status(record, "failed", error_message=str(exc))
                self._move_file(video_path, Path(self.settings.failed_folder) / video_path.name)
                logger.exception("Upload failed for {}: {}", video_path.name, exc)

        return processed

    @staticmethod
    def _move_file(source: Path, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.exists():
            shutil.move(str(source), str(destination))
