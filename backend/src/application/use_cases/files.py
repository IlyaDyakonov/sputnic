import mimetypes
from pathlib import Path
from typing import AsyncIterator
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.file_storage import FileStorage
from src.infrastructure.repositories.file_repo import FileRepository
from src.models import StoredFile


class FileUseCaseError(Exception):
    pass


class FileNotFoundError(FileUseCaseError):
    pass


class EmptyFileError(FileUseCaseError):
    pass


class StoredFileMissingError(FileUseCaseError):
    pass


class FileService:
    def __init__(self, session: AsyncSession, storage: FileStorage):
        self.repo = FileRepository(session)
        self.storage = storage

    async def list_files(self) -> list[StoredFile]:
        return await self.repo.list_files()

    async def get_file(self, file_id: str) -> StoredFile:
        file_item = await self.repo.get_by_id(file_id)
        if not file_item:
            raise FileNotFoundError("File not found")
        return file_item

    async def create_file(
        self,
        title: str,
        original_name: str | None,
        mime_type: str | None,
        chunks: AsyncIterator[bytes],
    ) -> StoredFile:
        file_id = str(uuid4())
        suffix = Path(original_name or "").suffix
        stored_name = f"{file_id}{suffix}"
        size = await self.storage.save_stream(stored_name=stored_name, chunks=chunks)
        if size == 0:
            await self.storage.delete_if_exists(stored_name)
            raise EmptyFileError("File is empty")

        file_item = StoredFile(
            id=file_id,
            title=title,
            original_name=original_name or stored_name,
            stored_name=stored_name,
            mime_type=mime_type or mimetypes.guess_type(stored_name)[0] or "application/octet-stream",
            size=size,
            processing_status="uploaded",
        )
        try:
            return await self.repo.create(file_item)
        except Exception:
            await self.storage.delete_if_exists(stored_name)
            raise

    async def update_file(self, file_id: str, title: str) -> StoredFile:
        file_item = await self.get_file(file_id)
        file_item.title = title
        return await self.repo.update(file_item)

    async def delete_file(self, file_id: str) -> None:
        file_item = await self.get_file(file_id)
        await self.storage.delete_if_exists(file_item.stored_name)
        await self.repo.delete(file_item)

    async def get_file_path(self, file_id: str) -> tuple[StoredFile, Path]:
        file_item = await self.get_file(file_id)
        if not await self.storage.exists(file_item.stored_name):
            raise StoredFileMissingError("Stored file not found")
        return file_item, self.storage.resolve_path(file_item.stored_name)
