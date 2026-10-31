from __future__ import annotations

import importlib
from io import BytesIO
from pathlib import Path

from starlette.requests import Request
from starlette.datastructures import UploadFile


def load_api_module(tmp_path: Path, monkeypatch):  # noqa: ANN001,ANN201
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{(tmp_path / 'test.db').as_posix()}")
    monkeypatch.setenv("UPLOAD_FOLDER", "videos")
    monkeypatch.setenv("UPLOADED_FOLDER", "uploaded")
    monkeypatch.setenv("FAILED_FOLDER", "failed")

    from app.config.settings import get_settings

    get_settings.cache_clear()
    from app.database import base

    importlib.reload(base)
    from app.api import main

    return importlib.reload(main)


def test_dashboard_homepage_renders(tmp_path: Path, monkeypatch) -> None:  # noqa: ANN001
    module = load_api_module(tmp_path, monkeypatch)
    request = Request({"type": "http", "method": "GET", "path": "/", "headers": [], "query_string": b""})

    response = module.dashboard(request)

    assert response.status_code == 200
    assert "YouTube AI Automation Agent" in response.body.decode()


def test_upload_endpoint_stores_mp4(tmp_path: Path, monkeypatch) -> None:  # noqa: ANN001
    module = load_api_module(tmp_path, monkeypatch)
    upload = UploadFile(filename="demo.mp4", file=BytesIO(b"fake-video-bytes"))

    response = module.upload_file(upload)

    assert response["file_name"] == "demo.mp4"
    assert (tmp_path / "videos" / "demo.mp4").exists()


def test_start_and_stop_actions_toggle_state(tmp_path: Path, monkeypatch) -> None:  # noqa: ANN001
    module = load_api_module(tmp_path, monkeypatch)

    def fake_start() -> None:
        module.agent.state.running = True

    def fake_stop() -> None:
        module.agent.state.running = False

    monkeypatch.setattr(module.agent, "start", fake_start)
    monkeypatch.setattr(module.agent, "stop", fake_stop)

    start_response = module.start_agent()
    stop_response = module.stop_agent()

    assert start_response["running"] is True
    assert stop_response["running"] is False
