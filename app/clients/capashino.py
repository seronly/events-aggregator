from httpx import AsyncClient, HTTPError

from app.errors.capashino import CapashinoError


class CapashinoClient:
    def __init__(self, base_url: str, api_key: str = "", timeout: float = 15.0) -> None:
        headers = {"x-api-key": api_key} if api_key else {}
        self._client = AsyncClient(
            base_url=base_url.rstrip("/"),
            headers=headers,
            timeout=timeout,
            follow_redirects=True,
        )

    async def send_notification(self, payload: dict) -> bool:
        try:
            response = await self._client.post("/api/notifications", json=payload)
        except HTTPError as exception:
            raise CapashinoError(
                f"Connection error with Capashino: {exception}"
            ) from exception

        if response.status_code in (201, 409):
            return True

        if response.status_code in (400, 401, 422):
            raise CapashinoError(
                f"Capashino reject request with status code {response.status_code}"
            )

        raise CapashinoError(
            f"Capashino unavailable. Status code: {response.status_code}",
        )
