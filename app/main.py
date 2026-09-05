from fastapi import FastAPI

from app.api.routers import events, sync, tickets
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
)

app.include_router(events.router)
app.include_router(sync.router)
app.include_router(tickets.router)


@app.get("/api/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
