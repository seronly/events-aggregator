from uuid import UUID

from fastapi import APIRouter, Depends, Request

from app.api.deps import get_events_service, get_seats_service
from app.domain.entities import Event
from app.schemas.events import (
    EventsDetailSchema,
    EventsListItemSchema,
    EventsListSchema,
    EventsQuerySchema,
    EventsSeatsSchema,
)
from app.schemas.place import PlaceDetailSchema, PlaceSchema
from app.services.events import EventService
from app.services.seats import SeatsService

router = APIRouter(prefix="/api/events", tags=["events"])


def _to_list_item(event: Event) -> EventsListItemSchema:
    return EventsListItemSchema(
        id=event.id,
        name=event.name,
        place=PlaceSchema(
            id=event.place.id,
            name=event.place.name,
            city=event.place.city,
            address=event.place.address,
        ),
        event_time=event.event_time,
        registration_deadline=event.registration_deadline,
        status=event.status,
        number_of_visitors=event.number_of_visitors,
    )


def _to_detail(event: Event) -> EventsDetailSchema:
    return EventsDetailSchema(
        id=event.id,
        name=event.name,
        place=PlaceDetailSchema(
            id=event.place.id,
            name=event.place.name,
            city=event.place.city,
            address=event.place.address,
            seats_pattern=event.place.seats_pattern,
        ),
        event_time=event.event_time,
        registration_deadline=event.registration_deadline,
        status=event.status,
        number_of_visitors=event.number_of_visitors,
    )


def _page_url(request: Request, page: int, page_size: int) -> str:
    url = request.url.include_query_params(page=page, page_size=page_size)
    return str(url)


@router.get("", response_model=EventsListSchema)
async def get_events(
    request: Request,
    data: EventsQuerySchema = Depends(),
    events: EventService = Depends(get_events_service),
):
    list_events, count = await events.get_events(
        data.date_from, data.page, data.page_size
    )

    has_next = data.page * data.page_size < count
    has_previous = data.page > 1

    return EventsListSchema(
        count=count,
        next=_page_url(request, data.page + 1, data.page_size) if has_next else None,
        previous=_page_url(request, data.page - 1, data.page_size)
        if has_previous
        else None,
        results=[_to_list_item(event) for event in list_events],
    )


@router.get("/{event_id}", response_model=EventsDetailSchema)
async def get_event_detail(
    event_id: UUID, events: EventService = Depends(get_events_service)
):
    event = await events.get_event_detail(event_id=event_id)

    return EventsDetailSchema(
        id=event.id,
        name=event.name,
        place=PlaceDetailSchema(
            id=event.place.id,
            name=event.place.name,
            city=event.place.city,
            address=event.place.address,
            seats_pattern=event.place.seats_pattern,
        ),
        event_time=event.event_time,
        registration_deadline=event.registration_deadline,
        status=event.status,
        number_of_visitors=event.number_of_visitors,
    )


@router.get("/{event_id}/seats", response_model=EventsSeatsSchema)
async def get_event_seats_info(
    event_id: UUID, seats: SeatsService = Depends(get_seats_service)
):
    available_seats = await seats.get_seats(event_id=event_id)

    return EventsSeatsSchema(event_id=event_id, available_seats=available_seats)
