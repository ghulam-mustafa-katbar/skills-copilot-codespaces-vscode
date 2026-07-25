"""Database access helpers for video records."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import VideoRecord
from app.metadata.schemas import VideoMetadata


class VideoRepository:
    """Encapsulates persistence operations for videos."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_hash(self, sha256_hash: str) -> VideoRecord | None:
        """Return existing record by content hash if present."""

        stmt = select(VideoRecord).where(VideoRecord.sha256_hash == sha256_hash)
        return self.session.scalar(stmt)

    def create(
        self,
        file_name: str,
        file_path: str,
        sha256_hash: str,
        metadata: VideoMetadata,
        scheduled_publish_at: datetime | None = None,
    ) -> VideoRecord:
        """Persist a newly queued video."""

        record = VideoRecord(
            file_name=file_name,
            file_path=file_path,
            sha256_hash=sha256_hash,
            status="queued",
            title=metadata.title,
            description=metadata.description,
            tags=",".join(metadata.tags),
            hashtags=",".join(metadata.hashtags),
            keywords=",".join(metadata.keywords),
            category=metadata.category,
            language=metadata.language,
            visibility=metadata.visibility,
            scheduled_publish_at=scheduled_publish_at,
        )
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

    def list_records(self, limit: int = 100) -> list[VideoRecord]:
        """Return recent records ordered by newest first."""

        stmt = select(VideoRecord).order_by(VideoRecord.id.desc()).limit(limit)
        return list(self.session.scalars(stmt).all())

    def list_queued(self, limit: int = 50) -> list[VideoRecord]:
        """Return currently queued videos."""

        stmt = (
            select(VideoRecord)
            .where(VideoRecord.status == "queued")
            .order_by(VideoRecord.created_at.asc())
            .limit(limit)
        )
        return list(self.session.scalars(stmt).all())

    def update_status(
        self,
        record: VideoRecord,
        status: str,
        youtube_video_id: str | None = None,
        error_message: str | None = None,
    ) -> VideoRecord:
        """Update processing state and timestamps."""

        record.status = status
        record.error_message = error_message
        if youtube_video_id:
            record.youtube_video_id = youtube_video_id
        if status == "uploaded":
            record.uploaded_at = datetime.utcnow()
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record
