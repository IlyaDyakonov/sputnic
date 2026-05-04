import asyncio
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.file_storage import FileStorage
from src.domain.services.threat_rules import evaluate_threat_reasons
from src.infrastructure.repositories.alert_repo import AlertRepository
from src.infrastructure.repositories.file_repo import FileRepository
from src.models import Alert


async def count_text_metadata(path: Path) -> tuple[int, int]:
    def count() -> tuple[int, int]:
        line_count = 0
        char_count = 0
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            for line in handle:
                line_count += 1
                char_count += len(line)
        return line_count, char_count

    return await asyncio.to_thread(count)


async def count_pdf_pages(path: Path) -> int:
    marker = b"/Type /Page"

    def count() -> int:
        page_count = 0
        carry = b""
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                data = carry + chunk
                page_count += data.count(marker)
                carry = data[-len(marker) + 1 :]
        return max(page_count, 1)

    return await asyncio.to_thread(count)


class ScanPipelineService:
    def __init__(self, session: AsyncSession, storage: FileStorage):
        self.file_repo = FileRepository(session)
        self.alert_repo = AlertRepository(session)
        self.storage = storage

    async def scan_file_for_threats(self, file_id: str) -> bool:
        repo = self.file_repo
        file_item = await repo.get_by_id(file_id)
        if not file_item:
            return False

        file_item.processing_status = "processing"
        reasons = evaluate_threat_reasons(file_item)
        file_item.scan_status = "suspicious" if reasons else "clean"
        file_item.scan_details = ", ".join(reasons) if reasons else "no threats found"
        file_item.requires_attention = bool(reasons)
        await repo.update(file_item)
        return True

    async def extract_file_metadata(self, file_id: str) -> bool:
        repo = self.file_repo
        file_item = await repo.get_by_id(file_id)
        if not file_item:
            return False

        if not await self.storage.exists(file_item.stored_name):
            file_item.processing_status = "failed"
            file_item.scan_status = file_item.scan_status or "failed"
            file_item.scan_details = "stored file not found during metadata extraction"
            await repo.update(file_item)
            return True

        stored_path = self.storage.resolve_path(file_item.stored_name)
        metadata = {
            "extension": Path(file_item.original_name).suffix.lower(),
            "size_bytes": file_item.size,
            "mime_type": file_item.mime_type,
        }

        if file_item.mime_type.startswith("text/"):
            line_count, char_count = await count_text_metadata(stored_path)
            metadata["line_count"] = line_count
            metadata["char_count"] = char_count
        elif file_item.mime_type == "application/pdf":
            metadata["approx_page_count"] = await count_pdf_pages(stored_path)

        file_item.metadata_json = metadata
        file_item.processing_status = "processed"
        await repo.update(file_item)
        return True

    async def send_file_alert(self, file_id: str) -> bool:
        file_item = await self.file_repo.get_by_id(file_id)
        if not file_item:
            return False

        if file_item.processing_status == "failed":
            alert = Alert(file_id=file_id, level="critical", message="File processing failed")
        elif file_item.requires_attention:
            alert = Alert(
                file_id=file_id,
                level="warning",
                message=f"File requires attention: {file_item.scan_details}",
            )
        else:
            alert = Alert(file_id=file_id, level="info", message="File processed successfully")

        await self.alert_repo.create(alert)
        return True
