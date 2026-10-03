import uuid
from datetime import UTC, datetime
from uuid import UUID

from app.clients.events_provider import EventsProviderClient
from app.domain.entities import OutboxRecord, Ticket
from app.enums.event import EventStatus
from app.enums.outbox import OutboxTypes
from app.errors.events import (
    EventAlreadyOccurred,
    EventNotFound,
    EventUnexpectedStatus,
    RegistrationClosed,
)
from app.errors.tickets import (
    DuplicateIdempotencyKey,
    IdempotencyKeyConflict,
    TicketNotFound,
)
from app.repositories.protocols import (
    EventRepository,
    OutboxRepository,
    TicketRepository,
)


class TicketService:
    def __init__(
        self,
        client: EventsProviderClient,
        events: EventRepository,
        tickets: TicketRepository,
        outbox: OutboxRepository,
    ) -> None:
        self._client = client
        self._events = events
        self._tickets = tickets
        self._outbox = outbox

    async def register(
        self,
        event_id: UUID,
        first_name: str,
        last_name: str,
        email: str,
        seat: str,
        idempotency_key: str | None = None,
    ) -> UUID:

        if idempotency_key:
            existing = await self._tickets.get_by_idempotency_key(idempotency_key)
            if existing is not None:
                self._check_existing(
                    ticket=existing,
                    event_id=event_id,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    seat=seat,
                )
                return existing.id

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
        try:
            await self._tickets.create(ticket)
        except DuplicateIdempotencyKey:
            if not idempotency_key:
                raise

            winner = await self._tickets.get_by_idempotency_key(
                idempotency_key=idempotency_key
            )
            if winner is None:
                raise
            self._check_existing(
                    ticket=winner,
                    event_id=event_id,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    seat=seat,
                )
            return winner.id

        success_registration_message = (
            f"Вы успешно зарегистрированы на {event.name},"
            " {event.event_time:%d.%m.%Y %H:%M}, место {seat}"
        )
        record_id = uuid.uuid4()
        await self._outbox.create(
            record=OutboxRecord(
                id=record_id,
                event_type=OutboxTypes.NOTIFICATION,
                payload={
                    "message": success_registration_message,
                    "reference_id": str(ticket.id),
                    "idempotency_key": str(record_id),
                },
            )
        )

        return ticket.id

    async def unregister(self, ticket_id: UUID) -> bool:
        ticket = await self._tickets.get(ticket_id=ticket_id)

        if ticket is None:
            raise TicketNotFound()

        event = await self._events.get_by_id(event_id=ticket.event_id)

        if event is None:
            raise EventNotFound()

        if event.event_time < datetime.now(UTC):
            raise EventAlreadyOccurred()

        unregister_response = await self._client.unregister(
            str(event.id), str(ticket.provider_ticket_id)
        )
        if unregister_response.success:
            await self._tickets.delete_by_id(ticket_id=ticket_id)

        return unregister_response.success


    def _check_existing(
        self,
        ticket: Ticket,
        event_id: UUID,
        first_name: str,
        last_name: str,
        email: str,
        seat: str,
    ) -> None:
        if (
            ticket.event_id,
            ticket.first_name,
            ticket.last_name,
            ticket.email,
            ticket.seat,
        ) != (event_id, first_name, last_name, email, seat):
            raise IdempotencyKeyConflict(ticket.idempotency_key)
