from pathlib import Path

from src.config import STORAGE_DIR


def save_file(stored_name: str, content: bytes) -> Path:
    stored_path = STORAGE_DIR / stored_name
    stored_path.write_bytes(content)
    return stored_path


def delete_file_if_exists(stored_name: str) -> None:
    stored_path = STORAGE_DIR / stored_name
    if stored_path.exists():
        stored_path.unlink()


def resolve_file_path(stored_name: str) -> Path:
    return STORAGE_DIR / stored_name
