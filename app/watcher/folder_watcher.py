"""Watchdog-based folder watcher for incoming videos."""

from pathlib import Path
from threading import Event

from loguru import logger
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class NewVideoEventHandler(FileSystemEventHandler):
    """React to newly created MP4 files."""

    def __init__(self, callback: callable) -> None:
        super().__init__()
        self.callback = callback

    def on_created(self, event) -> None:  # type: ignore[override]
        if event.is_directory:
            return
        file_path = Path(event.src_path)
        if file_path.suffix.lower() == ".mp4":
            logger.info("Detected new video: {}", file_path)
            self.callback(file_path)


class FolderWatcher:
    """Manages watchdog observer lifecycle."""

    def __init__(self, folder: str, callback: callable) -> None:
        self.folder = folder
        self.callback = callback
        self._observer = Observer()
        self._stop_event = Event()

    def start(self) -> None:
        handler = NewVideoEventHandler(self.callback)
        self._observer.schedule(handler, self.folder, recursive=False)
        self._observer.start()
        logger.info("Watching folder: {}", self.folder)

    def stop(self) -> None:
        self._stop_event.set()
        self._observer.stop()
        self._observer.join()
        logger.info("Stopped watcher")
