from fastapi import APIRouter

router = APIRouter(tags=["glitchtip"])


@router.get("/api/glitchtip/trigger-error")
async def trigger_error() -> None:
    raise RuntimeError("Test error for testing glitchtip")
