from pathlib import Path

from app.utils.hashing import calculate_sha256


def test_calculate_sha256_consistent(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.mp4"
    file_path.write_bytes(b"video-content")

    first = calculate_sha256(file_path)
    second = calculate_sha256(file_path)

    assert first == second
    assert len(first) == 64
