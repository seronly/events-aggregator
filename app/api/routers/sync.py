
from fastapi import APIRouter

router = APIRouter(prefix="/api/sync", tags=["sync"])

@router.post("/trigger")
async def manual_sync():
    ...
