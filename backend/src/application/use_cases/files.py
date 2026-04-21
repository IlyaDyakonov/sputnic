import mimetypes
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from src.config import DB_URL, STORAGE_DIR
from src.infrastructure.db.session import async_session_maker
from src.infrastructure.repositories.alert_repo import AlertRepository
from src.infrastructure.repositories.file_repo import FileRepository
from src.infrastructure.storage.local_storage import delete_file_if_exists, resolve_file_path, save_file
from src.models import Alert, StoredFile


async def list_files() -> list[StoredFile]:
    async with async_session_maker() as session:
        return await FileRepository(session).list_files()


async def list_alerts() -> list[Alert]:
    async with async_session_maker() as session:
        return await AlertRepository(session).list_alerts()


async def get_file(file_id: str) -> StoredFile:
    async with async_session_maker() as session:
        file_item = await FileRepository(session).get_by_id(file_id)
        if not file_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
        return file_item


async def create_file(title: str, upload_file: UploadFile) -> StoredFile:
    content = await upload_file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty")

    file_id = str(uuid4())
    suffix = Path(upload_file.filename or "").suffix
    stored_name = f"{file_id}{suffix}"
    save_file(stored_name=stored_name, content=content)

    file_item = StoredFile(
        id=file_id,
        title=title,
        original_name=upload_file.filename or stored_name,
        stored_name=stored_name,
        mime_type=upload_file.content_type or mimetypes.guess_type(stored_name)[0] or "application/octet-stream",
        size=len(content),
        processing_status="uploaded",
    )
    async with async_session_maker() as session:
        return await FileRepository(session).create(file_item)


async def update_file(file_id: str, title: str) -> StoredFile:
    async with async_session_maker() as session:
        repo = FileRepository(session)
        file_item = await repo.get_by_id(file_id)
        if not file_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
        file_item.title = title
        return await repo.update(file_item)


async def delete_file(file_id: str) -> None:
    async with async_session_maker() as session:
        repo = FileRepository(session)
        file_item = await repo.get_by_id(file_id)
        if not file_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
        delete_file_if_exists(file_item.stored_name)
        await repo.delete(file_item)


async def get_file_path(file_id: str) -> tuple[StoredFile, Path]:
    file_item = await get_file(file_id)
    stored_path = resolve_file_path(file_item.stored_name)
    if not stored_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stored file not found")
    return file_item, stored_path


async def create_alert(file_id: str, level: str, message: str) -> Alert:
    alert = Alert(file_id=file_id, level=level, message=message)
    async with async_session_maker() as session:
        return await AlertRepository(session).create(alert)


# Compatibility exports for step-by-step migration.
__all__ = [
    "DB_URL",
    "STORAGE_DIR",
    "create_alert",
    "create_file",
    "delete_file",
    "get_file",
    "get_file_path",
    "list_alerts",
    "list_files",
    "update_file",
]
