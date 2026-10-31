# YouTube AI Automation Agent

A production-ready, modular AI-powered automation system for YouTube Shorts. Place videos in a folder and the agent detects, enriches metadata with AI, schedules uploads, uploads via YouTube API, and tracks lifecycle in SQLite.

## Project Overview

The agent automates end-to-end Shorts publishing:
- Detects new `.mp4` files in `videos/`
- Prevents duplicates using SHA256
- Generates SEO metadata (title, description, tags, hashtags, keywords)
- Optionally generates thumbnails from video frames
- Uploads to YouTube Data API v3 with OAuth
- Supports scheduled publishing
- Stores metadata and status in SQLite
- Exposes FastAPI dashboard endpoints
- Exposes Typer CLI for operations

## Architecture

Clean architecture with separated concerns:
- **Config Layer**: environment settings and runtime paths
- **Core Layer**: logging/bootstrap
- **Data Layer**: SQLAlchemy models + repository
- **AI Layer**: Ollama provider + SEO generator
- **Service Layer**: orchestration, queueing, upload lifecycle
- **Integration Layer**: YouTube API, filesystem watcher, scheduler
- **Interface Layer**: FastAPI + CLI

## Features

1. Folder Watcher (Watchdog)
2. AI SEO Generator (Ollama default)
3. Metadata storage (SQLite + SQLAlchemy)
4. Upload Manager (OAuth + retries ready architecture)
5. Professional logging (console + rotating file logs)
6. Dashboard API (`/videos`, `/uploads`, `/status`, `/logs`, `/settings`)
7. CLI commands (`start`, `stop`, `upload`, `watch`, `status`, `logs`, `config`, `serve`)
8. Scheduler (interval + cron support)
9. Duplicate detection (SHA256)
10. Thumbnail generation (first frame)
11. AI provider abstraction for future OpenAI/Claude/Gemini providers

## Folder Structure

```text
youtube-ai-agent/
app/
    api/
    ai/
    cli/
    config/
    core/
    database/
    metadata/
    scheduler/
    seo/
    services/
    thumbnails/
    utils/
    watcher/
    youtube/
    logs/
videos/
uploaded/
failed/
thumbnails/
generated/
database/
tests/
scripts/
docs/
README.md
requirements.txt
.env.example
Dockerfile
docker-compose.yml
.gitignore
LICENSE
```

## Installation

### 1) Python
Install Python 3.12+

### 2) Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
```

### 3) Dependencies
```bash
pip install -r requirements.txt
```

### 4) FFmpeg
- Linux: `sudo apt install ffmpeg`
- Mac: `brew install ffmpeg`
- Windows: install from ffmpeg.org and add to PATH

## Google Cloud / YouTube API Setup

1. Create/select a Google Cloud project
2. Enable **YouTube Data API v3**
3. Configure OAuth consent screen
4. Create OAuth client credentials (Desktop App)
5. Download `client_secret.json`
6. Place it in the project root
7. On first upload, browser-based OAuth runs and stores `token.json`

## Environment Configuration

```bash
cp .env.example .env
```

Set required values:
- `YOUTUBE_CLIENT_SECRET`
- `YOUTUBE_CLIENT_ID`
- `DATABASE_URL`
- `OLLAMA_URL`
- `OLLAMA_MODEL`
- `UPLOAD_INTERVAL`
- `UPLOAD_FOLDER`
- `UPLOADED_FOLDER`
- `FAILED_FOLDER`
- `LOG_LEVEL`

## Ollama Setup

Install Ollama: https://ollama.com/download

```bash
ollama serve
ollama pull llama3
```

Change model via `.env`:
```env
OLLAMA_MODEL=qwen
```

## Run Application

### CLI
```bash
python -m app.cli.main start
python -m app.cli.main upload
python -m app.cli.main watch
python -m app.cli.main status
python -m app.cli.main logs --tail 100
python -m app.cli.main config
```

### FastAPI Dashboard
```bash
python -m app.cli.main serve --host 0.0.0.0 --port 8000
```

API docs:
- Swagger UI: `http://localhost:8000/docs`
- Web Dashboard UI: `http://localhost:8000/`

## Web Dashboard

The dashboard provides a full browser-based control center for the automation agent:
- Start/stop the watcher and scheduler
- Trigger scan/process/full-cycle actions
- Upload `.mp4` files directly from browser
- View pipeline metrics and recent logs
- Track recent video records and upload status

## API Endpoints

- `GET /`: web dashboard interface
- `GET /videos`: list stored video metadata
- `GET /uploads`: status counts
- `GET /status`: runtime service state
- `GET /logs`: tail logs
- `GET /settings`: non-sensitive config
- `POST /upload`: upload `.mp4` file to watch folder
- `POST /actions/start`: start watcher + scheduler
- `POST /actions/stop`: stop watcher + scheduler
- `POST /actions/scan`: scan and queue new videos
- `POST /actions/process`: process queued videos
- `POST /actions/run-once`: run scan + process sequence

## Scheduler

- Interval scheduling is enabled via `UPLOAD_INTERVAL` minutes.
- Cron scheduling support is available through `UploadScheduler.schedule_cron(...)`.

## How Uploads Work

1. User drops `.mp4` files into `videos/`
2. SHA256 hash is generated
3. Duplicate check is performed against SQLite records
4. AI metadata is generated
5. Video is queued and scheduled
6. Upload manager uploads to YouTube API
7. Status persisted (`queued`, `uploaded`, `failed`)
8. File moved to `uploaded/` or `failed/`

## AI Metadata Workflow

- `SEOGenerator` sends prompt to Ollama API (`/api/generate`)
- Expects strict JSON metadata
- If AI response fails, fallback metadata is generated from filename

## Docker Deployment

### Docker
```bash
docker build -t youtube-ai-agent .
docker run --env-file .env -p 8000:8000 youtube-ai-agent
```

### Docker Compose
```bash
docker compose up --build
```

## OS Notes

- Linux, macOS, and Windows are supported
- Ensure FFmpeg and Python 3.12+ are installed
- For Windows path consistency, keep project in a standard writable directory

## Troubleshooting

### OAuth errors
- Confirm OAuth credentials are desktop app credentials
- Ensure `client_secret.json` path is correct

### Upload failures
- Verify account/channel access
- Check API quota and logs in `app/logs/errors.log`

### Ollama errors
- Ensure `ollama serve` is running
- Verify selected model is pulled

## FAQ

**Q: Can I use OpenAI/Claude/Gemini?**
A: Architecture supports extension through provider abstraction in `app/ai`.

**Q: How are duplicates detected?**
A: Using SHA256 hash of file content before queueing.

## Future Roadmap

- OpenAI/Claude/Gemini providers
- Richer analytics dashboard
- Queue priority and batch strategies
- Multi-channel publishing
- Web UI with auth

## Contribution Guide

1. Fork and create a feature branch
2. Add tests for changes
3. Run `pytest`
4. Open PR with clear summary

## License

MIT (see `LICENSE`)
