from time import monotonic
from uuid import UUID

from app.clients.events_provider import EventsProviderClient
from app.enums.event import EventStatus
from app.errors.events import EventNotFound, EventUnexpectedStatus
from app.repositories.protocols import EventRepository

_CACHE: dict[UUID, tuple[float, list[str]]] = {}
_CACHE_TTL_SECONDS = 30.0

class SeatsService:
    def __init__(
        self,
        client: EventsProviderClient,
        events_repo: EventRepository,
    ):
        self._client = client
        self._events_repo = events_repo

    async def get_seats(self, event_id: UUID) -> list[str]:
        cached = _CACHE.get(event_id)
        now = monotonic()

        if cached is not None and now - cached[0] < _CACHE_TTL_SECONDS:
            return cached[1]

        event = await self._events_repo.get_by_id(event_id=event_id)

        if not event:
            raise EventNotFound

        if event.status != EventStatus.PUBLISHED:
            raise EventUnexpectedStatus

        available_seats = await self._client.get_seats(event_id=str(event_id))
        _CACHE[event_id] = (now, available_seats.seats)
        return available_seats.seats


