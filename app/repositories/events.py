from datetime import date
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain import entities
from app.enums.event import EventStatus
from app.models.events import Event


def _to_domain(sql_event: Event) -> entities.Event:
    place = sql_event.place
    return entities.Event(
        id=sql_event.id,
        name=sql_event.name,
        place=entities.Place(
            id=place.id,
            name=place.name,
            city=place.city,
            address=place.address,
            seats_pattern=place.seats_pattern,
        ),
        event_time=sql_event.event_time,
        registration_deadline=sql_event.registration_deadline,
        status=EventStatus(sql_event.status),
        number_of_visitors=sql_event.number_of_visitors,
        changed_at=sql_event.changed_at,
    )


class SqlAlchemyEventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, event_id: UUID) -> Event | None:
        stmt = (
            select(Event).options(selectinload(Event.place)).where(Event.id == event_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert(self, event: entities.Event) -> None:
        stmt = insert(Event).values(
            id=event.id,
            name=event.name,
            place_id=event.place.id,
            event_time=event.event_time,
            registration_deadline=event.registration_deadline,
            status=event.status,
            number_of_visitors=event.number_of_visitors,
            changed_at=event.changed_at,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=[Event.id],
            set_={
                "name": stmt.excluded.name,
                "place_id": stmt.excluded.place_id,
                "event_time": stmt.excluded.event_time,
                "registration_deadline": stmt.excluded.registration_deadline,
                "status": stmt.excluded.status,
                "number_of_visitors": stmt.excluded.number_of_visitors,
                "changed_at": stmt.excluded.changed_at,
            },
        )
        await self.session.execute(stmt)

    async def get_list_paginated(
        self, date_from: date | None = None, page: int = 1, page_size: int = 20
    ) -> list[entities.Event]:
        stmt = select(Event).options(selectinload(Event.place))
        if date_from is not None:
            stmt = stmt.where(Event.event_time >= date_from)

        stmt = (
            stmt.order_by(Event.event_time)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = (await self.session.execute(stmt)).scalars().all()
        return [_to_domain(row) for row in result]

    async def count(self, date_from: date | None = None) -> int:
        stmt = select(func.count()).select_from(Event)
        if date_from is not None:
            stmt = stmt.where(Event.event_time >= date_from)

        result = (await self.session.execute(stmt)).scalar_one()
        return result
