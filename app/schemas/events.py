import uuid
from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from app.schemas.place import PlaceSchema


class EventsStatus(StrEnum):
    NEW = "new"
    PUBLISHED = "published"


class EventsQuerySchema(BaseModel):
    date_from: date | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class EventsDetailSchema(BaseModel):
    id: uuid.UUID
    name: str
    place: PlaceSchema
    event_time: datetime
    registration_deadline: datetime
    status: EventsStatus
    number_of_visitors: int


class EventsListSchema(BaseModel):
    count: int
    next: str | None
    previous: str | None
    results: list[EventsDetailSchema]


class EventsSeatsSchema(BaseModel):
    event_id: uuid.UUID
    available_seats: list[str]
