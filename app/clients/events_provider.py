from httpx import AsyncClient

from app.core.config import settings
from app.schemas.events_provider import ProviderEventsPageSchema


class EventsProviderClient:
    def __init__(self) -> None:
        self.base_url = settings.events_provider_base_url
        self.api_key = settings.events_provider_api_key.get_secret_value()

    @property
    def headers(self) -> dict[str, str]:
        return {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }

    async def events(
        self, changed_at: str, cursor: str
    ) -> ProviderEventsPageSchema:
        url = self.base_url + "/api/events/"
        params = {
                "changed_at": changed_at,
                }

        async with AsyncClient(follow_redirects=True) as client:
            response = await client.get(url=url, params=params, headers=self.headers)

        response.raise_for_status()
        return ProviderEventsPageSchema.model_validate(response.json())

    async def register(
        self, event_id: str, first_name: str, last_name: str, email: str
    ): ...
