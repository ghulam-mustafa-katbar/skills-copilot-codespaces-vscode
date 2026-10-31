from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database.base import Base
from app.database.repository import VideoRepository
from app.metadata.schemas import VideoMetadata
from app.utils.hashing import calculate_sha256


def test_repository_prevents_duplicate_hash(tmp_path: Path) -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    local_session = sessionmaker(bind=engine, class_=Session)

    test_file = tmp_path / "video.mp4"
    test_file.write_bytes(b"duplicate")
    sha = calculate_sha256(test_file)

    metadata = VideoMetadata(
        title="Demo Title",
        description="Demo description for metadata testing.",
        tags=["a"],
        hashtags=["#a"],
        keywords=["a"],
        category="Education",
        language="en",
        visibility="private",
    )

    with local_session() as session:
        repository = VideoRepository(session)
        repository.create("video.mp4", str(test_file), sha, metadata)

        existing = repository.get_by_hash(sha)
        assert existing is not None
        assert existing.file_name == "video.mp4"
