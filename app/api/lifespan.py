import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.clients.capashino import CapashinoClient
from app.clients.events_provider import EventsProviderClient
from app.core.config import Settings
from app.workers.background_sync import BackgroundSyncWorker
from app.workers.outbox import OutboxWorker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Startup...")
    settings = Settings()
    app.state.provider_client = EventsProviderClient(
        base_url=settings.events_provider_base_url,
        api_key=settings.events_provider_api_key.get_secret_value(),
        timeout=settings.events_provider_timeout,
    )

    bg_worker = BackgroundSyncWorker(
        client=app.state.provider_client, interval=settings.bg_worker_sync_interval
    )
    app.state.bg_sync_worker = bg_worker
    bg_worker.start()

    outbox_worker = OutboxWorker(
            client=CapashinoClient(
                base_url=settings.capashino_base_url,
                api_key=settings.capashino_api_key.get_secret_value(),
                ),
            interval=settings.outbox_worker_interval,
            max_attempts=settings.outbox_max_attempts,
            )

    app.state.outbox_worker = outbox_worker
    outbox_worker.start()


    try:
        yield

    finally:
        await bg_worker.stop()
        await app.state.provider_client.aclose()
        await outbox_worker.stop()
