from datetime import date
from uuid import UUID

from app.domain.entities import Event
from app.errors.events import EventNotFound
from app.repositories.protocols import EventRepository


class EventService:
    def __init__(self, events: EventRepository) -> None:
        self.events = events

    async def get_events(
        self, date_from: date | None = None, page: int = 1, page_size: int = 20
    ) -> tuple[list[Event], int]:
        list_events = await self.events.get_list_paginated(
            date_from=date_from, page=page, page_size=page_size
        )
        count_events = await self.events.count(date_from=date_from)

        return list_events, count_events

    async def get_event_detail(self, event_id: UUID) -> Event:
        event = await self.events.get_by_id(event_id)

        if event is None:
            raise EventNotFound(event_id)

        return event
