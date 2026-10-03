from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import entities
from app.enums.outbox import OutboxStatus
from app.models.outbox import Outbox


def _to_domain(sql_outbox: Outbox) -> entities.OutboxRecord:
    return entities.OutboxRecord(
        id=sql_outbox.id,
        event_type=sql_outbox.event_type,
        payload=sql_outbox.payload,
        status=sql_outbox.status,
        attempts_number=sql_outbox.attempts_number,
        created_at=sql_outbox.created_at,
        changed_at=sql_outbox.changed_at,
    )


class SqlAlchemyOutboxRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, record: entities.OutboxRecord) -> None:
        record = Outbox(
            id=record.id,
            event_type=record.event_type,
            payload=record.payload,
            status=OutboxStatus.PENDING,
        )
        self.session.add(record)

    async def get_pending(self, limit: int) -> list[entities.OutboxRecord]:
        stmt = (
            select(Outbox)
            .where(Outbox.status == OutboxStatus.PENDING)
            .order_by(Outbox.created_at)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        result = (await self.session.execute(stmt)).scalars().all()
        return [_to_domain(row) for row in result]

    async def mark_sent(self, record_id: UUID) -> None:
        record = await self.session.get(Outbox, record_id)
        if record is not None:
            record.status = OutboxStatus.SENT

    async def mark_failed_attempt(self, record_id: UUID) -> None:
        record = await self.session.get(Outbox, record_id)
        if record is not None:
            record.attempts_number += 1

    async def mark_failed(self, record_id: UUID) -> None:
        record = await self.session.get(Outbox, record_id)
        if record is not None:
            record.status = OutboxStatus.FAILED

