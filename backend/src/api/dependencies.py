from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.use_cases.alerts import AlertService
from src.application.use_cases.files import FileService
from src.infrastructure.db.session import get_session
from src.infrastructure.storage.local_storage import LocalFileStorage

file_storage = LocalFileStorage()


def get_file_storage() -> LocalFileStorage:
    return file_storage


def get_file_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    storage: Annotated[LocalFileStorage, Depends(get_file_storage)],
) -> FileService:
    return FileService(session=session, storage=storage)


def get_alert_service(session: Annotated[AsyncSession, Depends(get_session)]) -> AlertService:
    return AlertService(session=session)
