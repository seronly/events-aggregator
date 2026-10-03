from enum import StrEnum


class OutboxTypes(StrEnum):
    NOTIFICATION = "notification"


class OutboxStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
