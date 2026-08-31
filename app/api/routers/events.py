from uuid import UUID

from fastapi import APIRouter, Depends

from app.schemas.events import (
    EventsDetailSchema,
    EventsListSchema,
    EventsQuerySchema,
    EventsSeatsSchema,
)

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("", response_model=EventsListSchema)
async def get_events(data: EventsQuerySchema = Depends()): ...


@router.get("/{event_id}", response_model=EventsDetailSchema)
async def get_event_detail(event_id: UUID): ...


@router.get("/{event_id}/seats", response_model=EventsSeatsSchema)
async def get_event_seats_info(event_id: UUID): ...
