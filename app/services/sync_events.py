import logging
from datetime import UTC, datetime

from app.clients.events_paginator import EventsPaginator
from app.clients.events_provider import EventsProviderClient
from app.domain.entities import Event, Place, SyncState
from app.enums.event import EventStatus
from app.enums.sync_state import SyncStatus
from app.repositories.protocols import EventRepository, PlaceRepository, SyncRepository
from app.schemas.events_provider import ProviderEventSchema

logger = logging.getLogger(__name__)


def _event_to_domain(provider_event: ProviderEventSchema) -> Event:
    place = Place(
        id=provider_event.place.id,
        name=provider_event.place.name,
        city=provider_event.place.city,
        address=provider_event.place.address,
        seats_pattern=provider_event.place.seats_pattern,
    )

    return Event(
        id=provider_event.id,
        name=provider_event.name,
        place=place,
        event_time=provider_event.event_time,
        registration_deadline=provider_event.registration_deadline,
        status=EventStatus(provider_event.status),
        number_of_visitors=provider_event.number_of_visitors,
        changed_at=provider_event.changed_at,
    )


class SyncEventsService:
    def __init__(
        self,
        client: EventsProviderClient,
        events: EventRepository,
        place: PlaceRepository,
        sync: SyncRepository,
    ) -> None:
        self._client = client
        self._events_repo = events
        self._place_repo = place
        self._sync_repo = sync

    async def sync(self) -> None:
        actual_sync_state = await self._sync_repo.get_state()
        last_changed_at = (
            actual_sync_state.last_changed_at
            if actual_sync_state.last_changed_at
            else datetime(2000, 1, 1, tzinfo=UTC)
        )

        paginator = EventsPaginator(
            client=self._client, changed_at=last_changed_at.date().isoformat()
        )

        await self._sync_repo.save_state(
            SyncState(
                last_sync_time=actual_sync_state.last_sync_time,
                last_changed_at=actual_sync_state.last_changed_at,
                sync_status=SyncStatus.RUNNING,
            )
        )

        try:
            async for provider_event in paginator:
                event = _event_to_domain(provider_event)
                await self._place_repo.upsert(event.place)
                await self._events_repo.upsert(event)
                last_changed_at = max(event.changed_at, last_changed_at)

        except Exception as e:
            logger.warning(e)
            await self._sync_repo.save_state(
                SyncState(datetime.now(UTC), last_changed_at, SyncStatus.FAILED, str(e))
            )
        else:
            await self._sync_repo.save_state(
                SyncState(datetime.now(UTC), last_changed_at, SyncStatus.SUCCESS)
            )
