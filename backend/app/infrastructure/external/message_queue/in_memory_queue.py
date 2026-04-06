import asyncio
import itertools
from typing import Any, Optional, Tuple

from app.domain.external.message_queue import MessageQueue


class InMemoryMessageQueue(MessageQueue):
    """Simple in-memory queue with replay support for standalone dev mode."""

    def __init__(self):
        self._messages: list[tuple[str, Any]] = []
        self._counter = itertools.count(1)
        self._condition = asyncio.Condition()

    async def put(self, message: Any) -> str:
        async with self._condition:
            message_id = f"{next(self._counter):020d}"
            self._messages.append((message_id, message))
            self._condition.notify_all()
            return message_id

    def _get_after(self, start_id: Optional[str]) -> Tuple[Optional[str], Any]:
        if not self._messages:
            return None, None

        if not start_id:
            return self._messages[0]

        for message_id, payload in self._messages:
            if message_id > start_id:
                return message_id, payload
        return None, None

    async def get(self, start_id: Optional[str] = None, block_ms: Optional[int] = None) -> Tuple[Optional[str], Any]:
        async with self._condition:
            message = self._get_after(start_id)
            if message[0] is not None:
                return message

            timeout = block_ms / 1000 if block_ms and block_ms > 0 else 0.05
            try:
                await asyncio.wait_for(self._condition.wait(), timeout=timeout)
            except asyncio.TimeoutError:
                return None, None
            return self._get_after(start_id)

    async def pop(self) -> Tuple[Optional[str], Any]:
        async with self._condition:
            if not self._messages:
                return None, None
            return self._messages.pop(0)

    async def clear(self) -> None:
        async with self._condition:
            self._messages.clear()

    async def is_empty(self) -> bool:
        return len(self._messages) == 0

    async def size(self) -> int:
        return len(self._messages)

    async def delete_message(self, message_id: str) -> bool:
        async with self._condition:
            original_size = len(self._messages)
            self._messages = [message for message in self._messages if message[0] != message_id]
            return len(self._messages) != original_size
