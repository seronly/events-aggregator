import datetime
import uuid

from sqlalchemy import DateTime, Integer, String, Uuid, func
from sqlalchemy.dialects.postgresql import JSON, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import BaseModel
from app.enums.outbox import OutboxStatus, OutboxTypes


class Outbox(BaseModel):
    __tablename__ = "outbox"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    event_type: Mapped[OutboxTypes] = mapped_column(
        String(64), default=OutboxTypes.NOTIFICATION
    )
    payload: Mapped[dict] = mapped_column(JSON().with_variant(JSONB(), "postgresql"))
    status: Mapped[OutboxStatus] = mapped_column(
        String(16), default=OutboxStatus.PENDING
    )
    attempts_number: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    changed_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
