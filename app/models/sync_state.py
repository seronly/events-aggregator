from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import BaseModel
from app.enums.sync_state import SyncStatus


class SyncState(BaseModel):
    __tablename__ = "sync_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    last_sync_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_changed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    sync_status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=SyncStatus.IDLE.value,
    )

    last_error: Mapped[str | None] = mapped_column(String(1024), nullable=True)
