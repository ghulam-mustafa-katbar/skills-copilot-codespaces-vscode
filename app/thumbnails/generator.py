"""Thumbnail generation utilities."""

from pathlib import Path

import cv2
from PIL import Image


def generate_thumbnail(video_path: Path, output_path: Path) -> Path:
    """Generate thumbnail from first video frame."""

    capture = cv2.VideoCapture(str(video_path))
    success, frame = capture.read()
    capture.release()
    if not success:
        raise ValueError(f"Unable to read frame from {video_path}")

    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    image.thumbnail((1080, 1920))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path, format="JPEG", quality=90)
    return output_path
