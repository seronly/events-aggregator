import asyncio
import contextlib
import logging

from app.clients.capashino import CapashinoClient
from app.core.config import settings
from app.core.db import session_maker
from app.errors.capashino import CapashinoError
from app.repositories.outbox import SqlAlchemyOutboxRepository

logger = logging.getLogger(__name__)


class OutboxWorker:
    def __init__(
        self, client: CapashinoClient, interval: int, max_attempts: int
    ) -> None:
        self._client = client
        self._interval = interval
        self._max_attempts = max_attempts
        self._task: asyncio.Task | None = None

    def start(self) -> None:
        self._task = asyncio.create_task(self._loop(), name="outbox-dispatcher")

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task

    async def _loop(self) -> None:
        while True:
            await self._run_once()
            await asyncio.sleep(self._interval)

    async def _run_once(self) -> None:
        try:
            async with session_maker() as session:
                async with session.begin():
                    outbox = SqlAlchemyOutboxRepository(session)
                    records = await outbox.get_pending(
                        limit=settings.outbox_limit_records
                    )

                    for record in records:
                        if record.attempts_number >= self._max_attempts:
                            await outbox.mark_failed(record_id=record.id)
                            continue

                        try:
                            async with session.begin_nested():
                                try:
                                    await self._client.send_notification(record.payload)
                                except CapashinoError:
                                    await outbox.mark_failed_attempt(
                                        record_id=record.id
                                    )
                                else:
                                    await outbox.mark_sent(record_id=record.id)
                        except Exception as e:
                            logger.exception(
                                "Unexpected error while process record in worker",
                                {"record_id": record.id, "exception": e},
                            )
        except Exception as e:
            logger.exception(
                "Unexpected error in outbox worker",
                {"exception": e},
            )
