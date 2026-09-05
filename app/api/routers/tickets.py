import uuid

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_ticket_service
from app.errors.events import (
    EventAlreadyOccurred,
    EventNotFound,
    EventUnexpectedStatus,
    RegistrationClosed,
)
from app.errors.tickets import SeatNotAvailable, TicketNotFound
from app.schemas.tickets import (
    TicketCreateQuerySchema,
    TicketCreateSchema,
    TicketDeleteSchema,
)
from app.services.tickets import TicketService

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


@router.post("/", response_model=TicketCreateSchema)
async def register(
    data: TicketCreateQuerySchema,
    tickets: TicketService = Depends(get_ticket_service),
):
    try:
        ticket_id = await tickets.register(
            event_id=data.event_id,
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            seat=data.seat,
        )
    except EventNotFound as e:
        raise HTTPException(status_code=404, detail="Event not found") from e
    except EventUnexpectedStatus as e:
        raise HTTPException(status_code=409, detail="Event unexpected status") from e
    except RegistrationClosed as e:
        raise HTTPException(status_code=409, detail="Registration closed") from e
    except SeatNotAvailable as e:
        raise HTTPException(status_code=409, detail="Seat not available") from e

    return TicketCreateSchema(ticket_id=ticket_id)


@router.delete("/{ticket_id}", response_model=TicketDeleteSchema)
async def unregister(
    ticket_id: uuid.UUID, tickets: TicketService = Depends(get_ticket_service)
):
    try:
        success = await tickets.unregister(ticket_id)
    except TicketNotFound as e:
        raise HTTPException(status_code=404, detail="Ticket not found") from e
    except EventAlreadyOccurred as e:
        raise HTTPException(status_code=409, detail="Event already occured") from e

    return TicketDeleteSchema(success=success)
