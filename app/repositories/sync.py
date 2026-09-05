from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import entities
from app.enums.sync_state import SyncStatus
from app.models.sync_state import SyncState


class SqlAlchemySyncRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_state(self) -> entities.SyncState:
        sync_state = await self.session.get(SyncState, 1)
        if sync_state is None:
            return entities.SyncState(
                last_sync_time=None, last_changed_at=None, sync_status=SyncStatus.IDLE
            )
        return entities.SyncState(
            last_sync_time=sync_state.last_sync_time,
            last_changed_at=sync_state.last_changed_at,
            sync_status=SyncStatus(sync_state.sync_status),
            last_error=sync_state.last_error,
        )

    async def save_state(self, state: entities.SyncState) -> None:
        stmt = insert(SyncState).values(
            id=1,
            last_sync_time=state.last_sync_time,
            last_changed_at=state.last_changed_at,
            sync_status=state.sync_status,
            last_error=state.last_error,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=[SyncState.id],
            set_={
                "last_sync_time": stmt.excluded.last_sync_time,
                "last_changed_at": stmt.excluded.last_changed_at,
                "sync_status": stmt.excluded.sync_status,
                "last_error": stmt.excluded.last_error,
            },
        )
        await self.session.execute(stmt)
