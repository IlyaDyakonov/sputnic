import asyncio
from pathlib import Path
from typing import AsyncIterator

from src.config import STORAGE_DIR


class LocalFileStorage:
    def __init__(self, root: Path = STORAGE_DIR):
        self.root = root

    def resolve_path(self, stored_name: str) -> Path:
        return self.root / stored_name

    async def save_stream(self, stored_name: str, chunks: AsyncIterator[bytes]) -> int:
        stored_path = self.resolve_path(stored_name)
        await asyncio.to_thread(stored_path.parent.mkdir, parents=True, exist_ok=True)
        size = 0
        handle = await asyncio.to_thread(stored_path.open, "wb")
        try:
            async for chunk in chunks:
                if not chunk:
                    continue
                size += len(chunk)
                await asyncio.to_thread(handle.write, chunk)
        except Exception:
            await asyncio.to_thread(handle.close)
            await self.delete_if_exists(stored_name)
            raise
        else:
            await asyncio.to_thread(handle.close)
        return size

    async def delete_if_exists(self, stored_name: str) -> None:
        stored_path = self.resolve_path(stored_name)
        if await asyncio.to_thread(stored_path.exists):
            await asyncio.to_thread(stored_path.unlink)

    async def exists(self, stored_name: str) -> bool:
        stored_path = self.resolve_path(stored_name)
        return await asyncio.to_thread(stored_path.exists)
