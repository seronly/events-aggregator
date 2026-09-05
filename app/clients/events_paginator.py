from collections.abc import AsyncIterator
from urllib.parse import parse_qs, urlparse

from app.clients.events_provider import EventsProviderClient
from app.schemas.events_provider import ProviderEventSchema, ProviderEventsPageSchema


class EventsPaginator:
    def __init__(self, client: EventsProviderClient, changed_at: str) -> None:
        self.client = client
        self.changed_at = changed_at
        self._cursor: str | None = None
        self._buffer: list[ProviderEventSchema] = []
        self._is_over: bool = False

    def __aiter__(self) -> AsyncIterator[ProviderEventSchema]:
        return self

    async def __anext__(self) -> ProviderEventSchema:
        while not self._buffer:
            if self._is_over:
                raise StopAsyncIteration

            page: ProviderEventsPageSchema = await self.client.events(
                changed_at=self.changed_at, cursor=self._cursor
            )
            self._buffer.extend(page.results)

            if page.next is None:
                self._is_over = True
            else:
                self._cursor = self._extract_cursor(page.next)

        return self._buffer.pop(0)

    def _extract_cursor(self, next_url: str | None) -> str | None:
        if not next_url:
            return None

        parsed = urlparse(next_url)
        return parse_qs(parsed.query).get("cursor", [None])[0]
