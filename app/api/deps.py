from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.events_provider import EventsProviderClient
from app.core.db import get_session
from app.repositories.events import SqlAlchemyEventRepository
from app.repositories.places import SqlAlchemyPlaceRepository
from app.repositories.protocols import EventRepository, PlaceRepository, SyncRepository
from app.repositories.sync import SqlAlchemySyncRepository
from app.services.sync_events import SyncEventsService


def get_event_repository(
    session: AsyncSession = Depends(get_session),
) -> EventRepository:
    return SqlAlchemyEventRepository(session)


def get_sync_repository(
    session: AsyncSession = Depends(get_session),
) -> SyncRepository:
    return SqlAlchemySyncRepository(session)


def get_place_repository(
    session: AsyncSession = Depends(get_session),
) -> PlaceRepository:
    return SqlAlchemyPlaceRepository(session)


def get_events_provider_client() -> EventsProviderClient:
    return EventsProviderClient()


def get_sync_events_service(
    client: EventsProviderClient = Depends(get_events_provider_client),
    events_repo: EventRepository = Depends(get_event_repository),
    place_repo: PlaceRepository = Depends(get_place_repository),
    sync_repo: SyncRepository = Depends(get_sync_repository),
) -> SyncEventsService:
    return SyncEventsService(
        client=client,
        events=events_repo,
        place=place_repo,
        sync=sync_repo,
    )


