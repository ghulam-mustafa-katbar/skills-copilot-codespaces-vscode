"""FastAPI dashboard API and web interface."""

from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config.settings import get_settings
from app.database.base import SessionLocal
from app.database.repository import VideoRepository
from app.services.agent import YouTubeAutomationAgent

settings = get_settings()
agent = YouTubeAutomationAgent(settings)
app = FastAPI(title=settings.app_name, version="1.0.0")

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request) -> HTMLResponse:
    """Serve web dashboard."""

    return templates.TemplateResponse(request=request, name="dashboard.html", context={"app_name": settings.app_name})


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
            "scheduled_publish_at": record.scheduled_publish_at,
            "error_message": record.error_message,
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


@app.post("/actions/start")
def start_agent() -> dict:
    """Start watcher and scheduler services."""

    if not agent.state.running:
        agent.start()
    return service_status()


@app.post("/actions/stop")
def stop_agent() -> dict:
    """Stop watcher and scheduler services."""

    if agent.state.running:
        agent.stop()
    return service_status()


@app.post("/actions/scan")
def scan_now() -> dict:
    """Queue new videos from upload folder."""

    queued = agent.scan_and_queue()
    return {"queued": queued, **service_status()}


@app.post("/actions/process")
def process_now() -> dict:
    """Process queued uploads immediately."""

    processed = agent.upload_now()
    return {"processed": processed, **service_status()}


@app.post("/actions/run-once")
def run_once() -> dict:
    """Run scan and process in sequence."""

    queued = agent.scan_and_queue()
    processed = agent.upload_now()
    return {"queued": queued, "processed": processed, **service_status()}


@app.post("/upload")
def upload_file(file: UploadFile = File(...)) -> dict:
    """Upload a local mp4 file into watched upload folder."""

    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    target_name = Path(file.filename).name
    if not target_name.lower().endswith(".mp4"):
        raise HTTPException(status_code=400, detail="Only .mp4 files are supported")

    destination = Path(settings.upload_folder) / target_name
    destination.parent.mkdir(parents=True, exist_ok=True)

    with destination.open("wb") as output:
        while True:
            chunk = file.file.read(1024 * 1024)
            if not chunk:
                break
            output.write(chunk)

    return {"message": "File uploaded", "file_name": target_name, "path": str(destination)}
