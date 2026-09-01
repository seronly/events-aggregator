import uuid

from fastapi import APIRouter

from app.schemas.tickets import (
    TicketCreateQuerySchema,
    TicketCreateSchema,
    TicketDeleteSchema,
)

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


@router.post("/", response_model=TicketCreateSchema)
async def register(data: TicketCreateQuerySchema): ...


@router.delete("/{ticket_id}", response_model=TicketDeleteSchema)
async def unregister(ticket_id: uuid.UUID): ...
