"""FastAPI dashboard API."""

from pathlib import Path

from fastapi import FastAPI

from app.config.settings import get_settings
from app.database.base import SessionLocal
from app.database.repository import VideoRepository
from app.services.agent import YouTubeAutomationAgent

settings = get_settings()
agent = YouTubeAutomationAgent(settings)
app = FastAPI(title=settings.app_name, version="1.0.0")


@app.get("/videos")
def list_videos(limit: int = 100) -> list[dict]:
    """List stored videos and metadata."""

    with SessionLocal() as session:
        records = VideoRepository(session).list_records(limit=limit)
    return [
        {
            "id": record.id,
            "file_name": record.file_name,
            "status": record.status,
            "youtube_video_id": record.youtube_video_id,
            "title": record.title,
            "uploaded_at": record.uploaded_at,
            "created_at": record.created_at,
        }
        for record in records
    ]


@app.get("/uploads")
def uploads_status() -> dict:
    """Return queued/upload status counts."""

    with SessionLocal() as session:
        records = VideoRepository(session).list_records(limit=1000)
    summary: dict[str, int] = {}
    for record in records:
        summary[record.status] = summary.get(record.status, 0) + 1
    return {"counts": summary, "total": len(records)}


@app.get("/status")
def service_status() -> dict:
    """Return current runtime service status."""

    return {
        "running": agent.state.running,
        "last_scan_count": agent.state.last_scan_count,
        "last_processed_count": agent.state.last_processed_count,
    }


@app.get("/logs")
def logs(tail: int = 100) -> dict:
    """Return last lines from application log file."""

    log_file = Path("app/logs/application.log")
    if not log_file.exists():
        return {"lines": []}
    lines = log_file.read_text(encoding="utf-8").splitlines()
    return {"lines": lines[-tail:]}


@app.get("/settings")
def current_settings() -> dict:
    """Return safe runtime settings subset."""

    return {
        "upload_interval": settings.upload_interval,
        "upload_folder": settings.upload_folder,
        "uploaded_folder": settings.uploaded_folder,
        "failed_folder": settings.failed_folder,
        "ollama_url": settings.ollama_url,
        "ollama_model": settings.ollama_model,
        "log_level": settings.log_level,
    }
