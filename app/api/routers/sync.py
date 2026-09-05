from fastapi import APIRouter, Depends

from app.api.deps import get_sync_events_service
from app.services.sync_events import SyncEventsService

router = APIRouter(prefix="/api/sync", tags=["sync"])


@router.post("/trigger")
async def manual_sync(
    sync_service: SyncEventsService = Depends(get_sync_events_service),
):

    await sync_service.sync()

    return {"status": "sync triggered"}
