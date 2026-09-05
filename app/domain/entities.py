import datetime
import uuid
from dataclasses import dataclass

from app.enums.event import EventStatus
from app.enums.sync_state import SyncStatus


@dataclass(slots=True)
class Place:
    id: uuid.UUID
    name: str
    city: str
    address: str
    seats_pattern: str


@dataclass(slots=True)
class Event:
    id: uuid.UUID
    name: str
    place: Place
    event_time: datetime.datetime
    registration_deadline: datetime.datetime
    status: EventStatus
    number_of_visitors: int
    changed_at: datetime.datetime

@dataclass(slots=True)
class SyncState:
    last_sync_time: datetime.datetime | None
    last_changed_at: datetime.datetime | None
    sync_status: SyncStatus
    last_error: str | None = None
