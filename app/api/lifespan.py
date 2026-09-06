import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.clients.events_provider import EventsProviderClient
from app.core.config import Settings
from app.workers.background_sync import BackgroundSyncWorker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_SYNC_INTERVAL = 24 * 60 * 60


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Startup...")
    settings = Settings()
    app.state.provider_client = EventsProviderClient(
        base_url=settings.events_provider_base_url,
        api_key=settings.events_provider_api_key.get_secret_value(),
        timeout=10,
    )

    bg_worker = BackgroundSyncWorker(
        client=app.state.provider_client, interval=_SYNC_INTERVAL
    )
    app.state.bg_sync_worker = bg_worker
    bg_worker.start()

    try:
        yield

    finally:
        await bg_worker.stop()
        await app.state.provider_client.aclose()
