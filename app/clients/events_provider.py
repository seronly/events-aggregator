from httpx import AsyncClient

from app.schemas.events_provider import (
    ProviderEventsPageSchema,
    ProviderRegisterSchema,
    ProviderSeatsSchema,
    ProviderUnregisterSchema,
)


class EventsProviderClient:
    def __init__(self, base_url: str, api_key: str = "", timeout: float = 15.0) -> None:
        headers = {"x-api-key": api_key} if api_key else {}
        self._client = AsyncClient(
            base_url=base_url.rstrip("/"),
            headers=headers,
            timeout=timeout,
            follow_redirects=True,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> EventsProviderClient:
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self.aclose()

    async def events(
        self, changed_at: str = "2000-01-01", cursor: str | None = None
    ) -> ProviderEventsPageSchema:
        url = "/api/events/"
        params = {
            "changed_at": changed_at,
        }

        if cursor is not None:
            params["cursor"] = cursor

        response = await self._client.get(url=url, params=params)

        response.raise_for_status()
        return ProviderEventsPageSchema.model_validate(response.json())

    async def get_seats(self, event_id: str) -> ProviderSeatsSchema:
        url = f"/api/events/{event_id}/seats/"

        response = await self._client.get(url=url)

        response.raise_for_status()
        return ProviderSeatsSchema.model_validate(response.json())

    async def register(
        self, event_id: str, first_name: str, last_name: str, email: str, seat: str
    ) -> ProviderRegisterSchema:
        url = f"/api/events/{event_id}/register/"

        params = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "seat": seat,
        }

        response = await self._client.post(url=url, json=params)

        response.raise_for_status()
        return ProviderRegisterSchema.model_validate(response.json())

    async def unregister(
        self, event_id: str, ticket_id: str
    ) -> ProviderUnregisterSchema:
        url = f"/api/events/{event_id}/unregister/"

        params = {"ticket_id": ticket_id}

        response = await self._client.request(method="DELETE", url=url, json=params)

        response.raise_for_status()
        return ProviderUnregisterSchema.model_validate(response.json())
