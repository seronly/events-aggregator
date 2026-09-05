from httpx import AsyncClient

from app.core.config import settings
from app.schemas.events_provider import (
    ProviderEventsPageSchema,
    ProviderRegisterSchema,
    ProviderSeatsSchema,
    ProviderUnregisterSchema,
)


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
        self, changed_at: str = "2000-01-01", cursor: str | None = None
    ) -> ProviderEventsPageSchema:
        url = self.base_url + "/api/events/"
        params = {
            "changed_at": changed_at,
        }

        if cursor is not None:
            params["cursor"] = cursor

        async with AsyncClient(follow_redirects=True) as client:
            response = await client.get(url=url, params=params, headers=self.headers)

        response.raise_for_status()
        return ProviderEventsPageSchema.model_validate(response.json())

    async def get_seats(self, event_id: str) -> ProviderSeatsSchema:
        url = self.base_url + f"/api/events/{event_id}/seats/"

        async with AsyncClient(follow_redirects=True) as client:
            response = await client.get(url=url, headers=self.headers)

        response.raise_for_status()
        return ProviderSeatsSchema.model_validate(response.json())

    async def register(
        self, event_id: str, first_name: str, last_name: str, email: str, seat: str
    ) -> ProviderRegisterSchema:
        url = self.base_url + f"/api/events/{event_id}/register/"

        params = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "seat": seat,
        }

        async with AsyncClient(follow_redirects=True) as client:
            response = await client.post(url=url, headers=self.headers, json=params)

        response.raise_for_status()
        return ProviderRegisterSchema.model_validate(response.json())

    async def unregister(
        self, event_id: str, ticket_id: str
    ) -> ProviderUnregisterSchema:
        url = self.base_url + f"/api/events/{event_id}/unregister/"

        params = {"ticket_id": ticket_id}

        async with AsyncClient(follow_redirects=True) as client:
            response = await client.request(
                method="DELETE", url=url, headers=self.headers, json=params
            )

        response.raise_for_status()
        return ProviderUnregisterSchema.model_validate(response.json())
