from pathlib import Path
from typing import AsyncIterator, Protocol


class FileStorage(Protocol):
    async def save_stream(self, stored_name: str, chunks: AsyncIterator[bytes]) -> int:
        """Persist chunks and return the number of written bytes."""
        ...

    async def delete_if_exists(self, stored_name: str) -> None:
        ...

    async def exists(self, stored_name: str) -> bool:
        ...

    def resolve_path(self, stored_name: str) -> Path:
        ...
