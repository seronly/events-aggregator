from datetime import date
from typing import Protocol
from uuid import UUID

from app.domain.entities import Event, Place, SyncState


class EventRepository(Protocol):
    async def get_by_id(self, event_id: UUID) -> Event | None: ...

    async def upsert(self, event: Event) -> None: ...

    async def get_list_paginated(
        self, date_from: date | None = None, page: int = 1, page_size: int = 20
    ) -> list[Event]: ...

    async def count(self, date_from: date | None = None) -> int: ...


class PlaceRepository(Protocol):
    async def upsert(self, place: Place) -> None: ...


class SyncRepository(Protocol):
    async def get_state(self) -> SyncState: ...

    async def save_state(self, state: SyncState) -> None: ...
