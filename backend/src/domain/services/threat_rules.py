from pathlib import Path
from typing import Protocol


class FileScanTarget(Protocol):
    original_name: str
    mime_type: str
    size: int


def evaluate_threat_reasons(file_item: FileScanTarget) -> list[str]:
    # Keep current MVP rules unchanged while isolating business logic.
    reasons: list[str] = []
    extension = Path(file_item.original_name).suffix.lower()

    if extension in {".exe", ".bat", ".cmd", ".sh", ".js"}:
        reasons.append(f"suspicious extension {extension}")

    if file_item.size > 10 * 1024 * 1024:
        reasons.append("file is larger than 10 MB")

    if extension == ".pdf" and file_item.mime_type not in {"application/pdf", "application/octet-stream"}:
        reasons.append("pdf extension does not match mime type")

    return reasons
