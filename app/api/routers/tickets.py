from fastapi import APIRouter

router = APIRouter(prefix="/api/tickets", tags=["tickets"])

@router.post("/")
async def register():
    ...

@router.delete("/{ticket_id}")
async def close():
    ...
