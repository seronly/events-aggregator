from typing import Protocol

from app.domain.entities import Event, Place, SyncState


class SyncRepository(Protocol):
    async def get_state(self) -> SyncState: ...

    async def save_state(self, state: SyncState) -> None: ...
