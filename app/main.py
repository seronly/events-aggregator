import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from starlette.responses import JSONResponse

from app.api.lifespan import lifespan
from app.api.routers import events, glitchtip, sync, tickets
from app.core.config import settings

if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        integrations=[FastApiIntegration(), StarletteIntegration()],
    )

app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
    version="2.0.0",
)

app.include_router(events.router)
app.include_router(sync.router)
app.include_router(tickets.router)
app.include_router(glitchtip.router)


# just for lms
@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    return JSONResponse(status_code=400, content={"detail": exc.errors()})


@app.get("/api/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
