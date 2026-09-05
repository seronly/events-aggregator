from enum import StrEnum


class EventStatus(StrEnum):
    NEW = "new"
    PUBLISHED = "published"
    FINISHED = "finished"
    REGISTRATION_CLOSED = "registration_closed"
