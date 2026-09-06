import asyncio
import contextlib
import logging

from app.clients.events_provider import EventsProviderClient
from app.core.db import session_maker
from app.repositories.events import SqlAlchemyEventRepository
from app.repositories.places import SqlAlchemyPlaceRepository
from app.repositories.sync import SqlAlchemySyncRepository
from app.services.sync_events import SyncEventsService

logger = logging.getLogger(__name__)


class BackgroundSyncWorker:
    def __init__(self, client: EventsProviderClient, interval: int) -> None:
        self._client = client
        self._interval = interval
        self._lock = asyncio.Lock()
        self._task: asyncio.Task | None = None

    def start(self) -> None:
        self._task = asyncio.create_task(self._loop(), name="events-sync-worker")
        logger.info("Background worker started", {"interval": self._interval})

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task

    async def trigger(self) -> None:
        await self._run_once()

    async def _loop(self) -> None:
        while True:
            await self._run_once()
            await asyncio.sleep(self._interval)

    async def _run_once(self) -> None:
        if self._lock.locked():
            logger.info("Background worker already started")
            return

        async with self._lock:
            try:
                async with session_maker() as session:
                    sync_events = SyncEventsService(
                        client=self._client,
                        place=SqlAlchemyPlaceRepository(session),
                        events=SqlAlchemyEventRepository(session),
                        sync=SqlAlchemySyncRepository(session),
                    )
                    await sync_events.sync()
            except Exception:
                logger.exception("Unexpected worker error")
