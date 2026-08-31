from fastapi import APIRouter

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("")
async def get_events(): ...

@router.get("/{event_id}")
async def get_event_detail(event_id: int): ...

@router.get("/{event_id}/seats")
async def get_event_seats_info(event_id: int): ...
