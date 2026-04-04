import asyncio
import logging
import uuid
from typing import Dict, Optional

from app.domain.external.message_queue import MessageQueue
from app.domain.external.task import Task, TaskRunner
from app.infrastructure.external.message_queue.in_memory_queue import InMemoryMessageQueue

logger = logging.getLogger(__name__)


class InMemoryTask(Task):
    """Standalone in-memory task runner used when Redis is unavailable."""

    _task_registry: Dict[str, "InMemoryTask"] = {}

    def __init__(self, runner: TaskRunner):
        self._runner = runner
        self._id = str(uuid.uuid4())
        self._execution_task: Optional[asyncio.Task] = None
        self._input_stream = InMemoryMessageQueue()
        self._output_stream = InMemoryMessageQueue()
        InMemoryTask._task_registry[self._id] = self

    @property
    def id(self) -> str:
        return self._id

    @property
    def done(self) -> bool:
        if self._execution_task is None:
            return True
        return self._execution_task.done()

    @property
    def input_stream(self) -> MessageQueue:
        return self._input_stream

    @property
    def output_stream(self) -> MessageQueue:
        return self._output_stream

    async def run(self) -> None:
        if self._execution_task is None or self._execution_task.done():
            self._execution_task = asyncio.create_task(self._execute_task())
            logger.info("Started standalone task %s", self._id)

    def cancel(self) -> bool:
        if self._execution_task and not self._execution_task.done():
            self._execution_task.cancel()
            self._cleanup_registry()
            return True

        self._cleanup_registry()
        return False

    async def _execute_task(self) -> None:
        try:
            await self._runner.run(self)
        except asyncio.CancelledError:
            logger.info("Standalone task %s cancelled", self._id)
        except Exception as exc:
            logger.error("Standalone task %s failed: %s", self._id, exc)
        finally:
            try:
                await self._runner.on_done(self)
            finally:
                self._cleanup_registry()

    def _cleanup_registry(self) -> None:
        InMemoryTask._task_registry.pop(self._id, None)

    @classmethod
    def get(cls, task_id: str) -> Optional["InMemoryTask"]:
        return cls._task_registry.get(task_id)

    @classmethod
    def create(cls, runner: TaskRunner) -> "InMemoryTask":
        return cls(runner)

    @classmethod
    async def destroy(cls) -> None:
        for task in list(cls._task_registry.values()):
            task.cancel()
            if task._runner:
                await task._runner.destroy()
        cls._task_registry.clear()
