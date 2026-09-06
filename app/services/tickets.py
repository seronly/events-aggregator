import uuid
from datetime import UTC, datetime
from uuid import UUID

from app.clients.events_provider import EventsProviderClient
from app.domain.entities import Ticket
from app.enums.event import EventStatus
from app.errors.events import (
    EventAlreadyOccurred,
    EventNotFound,
    EventUnexpectedStatus,
    RegistrationClosed,
)
from app.errors.tickets import TicketNotFound
from app.repositories.protocols import EventRepository, TicketRepository


class TicketService:
    def __init__(
        self,
        client: EventsProviderClient,
        events: EventRepository,
        tickets: TicketRepository,
    ) -> None:
        self._client = client
        self._events = events
        self._tickets = tickets

    async def register(
        self, event_id: UUID, first_name: str, last_name: str, email: str, seat: str
    ) -> UUID:
        event = await self._events.get_by_id(event_id)

        if event is None:
            raise EventNotFound(event_id)

        if event.status != EventStatus.PUBLISHED:
            raise EventUnexpectedStatus(event.status)

        if event.registration_deadline <= datetime.now(UTC):
            raise RegistrationClosed(event.id)

        provider_ticket_response = await self._client.register(
            event_id=str(event.id),
            first_name=first_name,
            last_name=last_name,
            email=email,
            seat=seat,
        )
        ticket = Ticket(
            id=uuid.uuid4(),
            provider_ticket_id=provider_ticket_response.ticket_id,
            event_id=event.id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            seat=seat,
        )
        ticket_id = await self._tickets.create(ticket)

        return ticket_id

    async def unregister(self, ticket_id: UUID) -> bool:
        ticket = await self._tickets.get_by_provider_ticket_id(ticket_id=ticket_id)

        if ticket is None:
            raise TicketNotFound()

        event = await self._events.get_by_id(event_id=ticket.event_id)

        if event is None:
            raise EventNotFound()

        if event.event_time < datetime.now(UTC):
            raise EventAlreadyOccurred()

        unregister_response = await self._client.unregister(
            str(event.id), str(ticket_id)

        )
        if unregister_response.success:
            await self._tickets.delete_by_provider_ticket_id(ticket_id=ticket_id)

        return unregister_response.success
