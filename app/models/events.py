import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import BaseModel

if TYPE_CHECKING:
    from .places import Place

class Event(BaseModel):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    place_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("places.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    event_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    registration_deadline: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    status: Mapped[str] = mapped_column(String(255), nullable=False)
    number_of_visitors: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    place: Mapped[Place] = relationship(back_populates="events")

