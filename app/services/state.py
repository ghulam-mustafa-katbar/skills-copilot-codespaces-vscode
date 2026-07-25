"""In-memory runtime state for API and CLI reporting."""

from dataclasses import dataclass


@dataclass
class RuntimeState:
    """Simple service status summary."""

    running: bool = False
    last_scan_count: int = 0
    last_processed_count: int = 0
