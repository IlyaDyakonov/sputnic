import asyncio

from src.application.use_cases.scan_pipeline import ScanPipelineService
from src.infrastructure.db.session import async_session_maker
from src.infrastructure.storage.local_storage import LocalFileStorage
from src.infrastructure.tasks.celery_app import celery_app

_worker_loop: asyncio.AbstractEventLoop | None = None
_storage = LocalFileStorage()


def run_in_worker_loop(coroutine):
    global _worker_loop
    if _worker_loop is None or _worker_loop.is_closed():
        _worker_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_worker_loop)
    return _worker_loop.run_until_complete(coroutine)


async def with_scan_service(method_name: str, file_id: str) -> bool:
    async with async_session_maker() as session:
        service = ScanPipelineService(session=session, storage=_storage)
        method = getattr(service, method_name)
        return await method(file_id)


@celery_app.task
def scan_file_for_threats(file_id: str) -> None:
    found = run_in_worker_loop(with_scan_service("scan_file_for_threats", file_id))
    if found:
        extract_file_metadata.delay(file_id)


@celery_app.task
def extract_file_metadata(file_id: str) -> None:
    found = run_in_worker_loop(with_scan_service("extract_file_metadata", file_id))
    if found:
        send_file_alert.delay(file_id)


@celery_app.task
def send_file_alert(file_id: str) -> None:
    run_in_worker_loop(with_scan_service("send_file_alert", file_id))
