
from fastapi import APIRouter, status

router = APIRouter(prefix="/api/sync", tags=["sync"])

@router.post("/trigger", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def manual_sync(): ...
