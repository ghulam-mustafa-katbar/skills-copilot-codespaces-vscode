"""CLI commands for operating the YouTube automation agent."""

import time

import typer
import uvicorn
from rich.console import Console
from rich.table import Table

from app.config.settings import get_settings
from app.database.base import SessionLocal
from app.database.repository import VideoRepository
from app.services.agent import YouTubeAutomationAgent

app = typer.Typer(help="YouTube AI Automation Agent CLI")
console = Console()
settings = get_settings()
agent = YouTubeAutomationAgent(settings)


@app.command()
def start() -> None:
    """Start watcher and scheduler loop."""

    agent.start()
    console.print("[green]Agent started. Press Ctrl+C to stop.[/green]")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        agent.stop()


@app.command()
def stop() -> None:
    """Stop active automation components."""

    if agent.state.running:
        agent.stop()
    console.print("[yellow]Agent stopped[/yellow]")


@app.command()
def upload() -> None:
    """Scan and upload now."""

    queued = agent.scan_and_queue()
    processed = agent.upload_now()
    console.print(f"[cyan]Queued: {queued}, Processed: {processed}[/cyan]")


@app.command()
def watch() -> None:
    """Only watch and queue videos without uploading."""

    agent.watcher.start()
    console.print("[green]Watching upload folder. Press Ctrl+C to stop.[/green]")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        agent.watcher.stop()


@app.command()
def status() -> None:
    """Display current queue and processing status."""

    with SessionLocal() as session:
        records = VideoRepository(session).list_records(limit=200)

    table = Table(title="YouTube Automation Status")
    table.add_column("ID")
    table.add_column("File")
    table.add_column("Status")
    table.add_column("YouTube ID")

    for record in records[:20]:
        table.add_row(str(record.id), record.file_name, record.status, record.youtube_video_id or "-")

    console.print(table)
    console.print(
        {
            "running": agent.state.running,
            "last_scan_count": agent.state.last_scan_count,
            "last_processed_count": agent.state.last_processed_count,
        }
    )


@app.command()
def logs(tail: int = 50) -> None:
    """Print recent application logs."""

    from pathlib import Path

    log_file = Path("app/logs/application.log")
    if not log_file.exists():
        console.print("No logs yet.")
        return

    for line in log_file.read_text(encoding="utf-8").splitlines()[-tail:]:
        console.print(line)


@app.command()
def config() -> None:
    """Show runtime config values (non-sensitive)."""

    safe_config = {
        "upload_interval": settings.upload_interval,
        "upload_folder": settings.upload_folder,
        "uploaded_folder": settings.uploaded_folder,
        "failed_folder": settings.failed_folder,
        "ollama_url": settings.ollama_url,
        "ollama_model": settings.ollama_model,
        "database_url": settings.database_url,
    }
    console.print(safe_config)


@app.command()
def serve(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Run the FastAPI dashboard server."""

    uvicorn.run("app.api.main:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    app()
