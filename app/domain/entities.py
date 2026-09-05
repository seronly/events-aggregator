import datetime
from dataclasses import dataclass


@dataclass(slots=True)
class SyncState:
    last_sync_time: datetime.datetime | None
    last_changed_at: datetime.datetime | None
    sync_status: SyncStatus
    last_error: str | None = None
