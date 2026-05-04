from typing import Annotated, AsyncIterator, NoReturn

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from starlette import status

from src.api.dependencies import get_file_service
from src.application.use_cases.files import (
    EmptyFileError,
    FileNotFoundError as UseCaseFileNotFoundError,
    FileService,
    StoredFileMissingError,
)
from src.infrastructure.tasks.workers import scan_file_for_threats
from src.schemas import FileItem, FileUpdate

router = APIRouter(tags=["files"])
CHUNK_SIZE = 1024 * 1024


async def iter_upload_chunks(file: UploadFile) -> AsyncIterator[bytes]:
    try:
        while chunk := await file.read(CHUNK_SIZE):
            yield chunk
    finally:
        await file.close()


def raise_http_error(error: Exception) -> NoReturn:
    if isinstance(error, EmptyFileError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    if isinstance(error, (UseCaseFileNotFoundError, StoredFileMissingError)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    raise error


@router.get("/files", response_model=list[FileItem])
async def list_files_view(file_service: Annotated[FileService, Depends(get_file_service)]):
    return await file_service.list_files()


@router.post("/files", response_model=FileItem, status_code=201)
async def create_file_view(
    title: Annotated[str, Form(...)],
    file: Annotated[UploadFile, File(...)],
    file_service: Annotated[FileService, Depends(get_file_service)],
):
    try:
        file_item = await file_service.create_file(
            title=title,
            original_name=file.filename,
            mime_type=file.content_type,
            chunks=iter_upload_chunks(file),
        )
    except (EmptyFileError, UseCaseFileNotFoundError, StoredFileMissingError) as error:
        raise_http_error(error)
    scan_file_for_threats.delay(file_item.id)
    return file_item


@router.get("/files/{file_id}", response_model=FileItem)
async def get_file_view(file_id: str, file_service: Annotated[FileService, Depends(get_file_service)]):
    try:
        return await file_service.get_file(file_id)
    except UseCaseFileNotFoundError as error:
        raise_http_error(error)


@router.patch("/files/{file_id}", response_model=FileItem)
async def update_file_view(
    file_id: str,
    payload: FileUpdate,
    file_service: Annotated[FileService, Depends(get_file_service)],
):
    try:
        return await file_service.update_file(file_id=file_id, title=payload.title)
    except UseCaseFileNotFoundError as error:
        raise_http_error(error)


@router.get("/files/{file_id}/download")
async def download_file(file_id: str, file_service: Annotated[FileService, Depends(get_file_service)]):
    try:
        file_item, stored_path = await file_service.get_file_path(file_id)
    except (UseCaseFileNotFoundError, StoredFileMissingError) as error:
        raise_http_error(error)
    return FileResponse(
        path=stored_path,
        media_type=file_item.mime_type,
        filename=file_item.original_name,
        status_code=status.HTTP_200_OK,
    )


@router.delete("/files/{file_id}", status_code=204)
async def delete_file_view(file_id: str, file_service: Annotated[FileService, Depends(get_file_service)]):
    try:
        await file_service.delete_file(file_id)
    except UseCaseFileNotFoundError as error:
        raise_http_error(error)
