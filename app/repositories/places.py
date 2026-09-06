from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import entities
from app.models.places import Place


def _to_domain(sql_place: Place) -> entities.Place:
    return entities.Place(
        id=sql_place.id,
        name=sql_place.name,
        city=sql_place.city,
        address=sql_place.address,
        seats_pattern=sql_place.seats_pattern,
    )

class SqlAlchemyPlaceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert(self, place: entities.Place) -> None:
        stmt = insert(Place).values(
            id=place.id,
            name=place.name,
            city=place.city,
            address=place.address,
            seats_pattern=place.seats_pattern,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=[Place.id],
            set_={
                "name": stmt.excluded.name,
                "city": stmt.excluded.city,
                "address": stmt.excluded.address,
                "seats_pattern": stmt.excluded.seats_pattern,
            },
        )
        await self.session.execute(stmt)
