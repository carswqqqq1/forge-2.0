import io
import uuid
from datetime import datetime, UTC
from typing import Any, BinaryIO, Dict, Optional, Tuple

from app.domain.external.file import FileStorage
from app.domain.models.file import FileInfo


class InMemoryFileStorage(FileStorage):
    """Lightweight in-memory file storage for standalone local development."""

    def __init__(self):
        self._files: Dict[str, tuple[bytes, FileInfo]] = {}

    @staticmethod
    def _read_bytes(file_data: BinaryIO | bytes | bytearray | memoryview) -> bytes:
        if isinstance(file_data, (bytes, bytearray, memoryview)):
            return bytes(file_data)

        if hasattr(file_data, "seek"):
            try:
                file_data.seek(0)
            except Exception:
                pass

        data = file_data.read()
        if isinstance(data, str):
            return data.encode("utf-8")
        return bytes(data)

    async def upload_file(
        self,
        file_data: BinaryIO,
        filename: str,
        user_id: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> FileInfo:
        file_id = uuid.uuid4().hex
        info = FileInfo(
            file_id=file_id,
            filename=filename,
            content_type=content_type,
            size=0,
            upload_date=datetime.now(UTC),
            metadata=metadata or {},
            user_id=user_id,
        )
        payload = self._read_bytes(file_data)
        info.size = len(payload)
        self._files[file_id] = (payload, info.model_copy(deep=True))
        return info.model_copy(deep=True)

    async def download_file(self, file_id: str, user_id: Optional[str] = None) -> Tuple[BinaryIO, FileInfo]:
        record = self._files.get(file_id)
        if not record:
            raise FileNotFoundError(f"File not found with ID: {file_id}")

        payload, info = record
        if user_id is not None and info.user_id != user_id:
            raise PermissionError(f"Access denied for file: {file_id}")

        return io.BytesIO(payload), info.model_copy(deep=True)

    async def delete_file(self, file_id: str, user_id: str) -> bool:
        record = self._files.get(file_id)
        if not record:
            return False

        _, info = record
        if info.user_id != user_id:
            return False

        del self._files[file_id]
        return True

    async def get_file_info(self, file_id: str, user_id: Optional[str] = None) -> Optional[FileInfo]:
        record = self._files.get(file_id)
        if not record:
            return None

        _, info = record
        if user_id is not None and info.user_id != user_id:
            return None

        return info.model_copy(deep=True)
