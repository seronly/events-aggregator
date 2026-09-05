import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import BaseModel

if TYPE_CHECKING:
    from .events import Event


class Place(BaseModel):
    __tablename__ = "places"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    seats_pattern: Mapped[str] = mapped_column(String(255), nullable=False)

    events: Mapped[list[Event]] = relationship(back_populates="place")
