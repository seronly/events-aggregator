from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import entities
from app.models.tickets import Ticket


def _to_domain(ticket: Ticket) -> entities.Ticket:
    return entities.Ticket(
        id=ticket.id,
        provider_ticket_id=ticket.external_ticket_id,
        event_id=ticket.event_id,
        first_name=ticket.first_name,
        last_name=ticket.last_name,
        email=ticket.email,
        seat=ticket.seat,
    )


class SqlAlchemyTicketRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, ticket: entities.Ticket) -> UUID:
        sql_ticket = Ticket(
            id=ticket.id,
            external_ticket_id=ticket.provider_ticket_id,
            event_id=ticket.event_id,
            first_name=ticket.first_name,
            last_name=ticket.last_name,
            seat=ticket.seat,
            email=ticket.email,
        )
        self.session.add(sql_ticket)

        await self.session.flush()

        return sql_ticket.id

    async def get(self, ticket_id: UUID) -> entities.Ticket | None:
        ticket = await self.session.get(Ticket, ticket_id)

        return _to_domain(ticket) if ticket else None

    async def delete_by_id(self, ticket_id: UUID) -> bool:
        ticket = await self.session.get(Ticket, ticket_id)

        if not ticket:
            return False

        await self.session.delete(ticket)
        await self.session.flush()

        return True
