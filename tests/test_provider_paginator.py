import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from app.clients.events_paginator import EventsPaginator
from app.clients.events_provider import EventsProviderClient
from app.schemas.events_provider import ProviderEventsPageSchema

_NOW = datetime(2026, 9, 5, tzinfo=UTC).isoformat()
_CHANGED_AT = "2000-01-01"


def _make_place_payload() -> dict:
    return {
        "id": str(uuid.uuid4()),
        "name": "Test Hall",
        "city": "Testville",
        "address": "1 Test Street",
        "seats_pattern": "A1-A10",
        "changed_at": _NOW,
        "created_at": _NOW,
    }


def _make_event_payload(event_id: str) -> dict:
    return {
        "id": event_id,
        "name": "Test Event",
        "place": _make_place_payload(),
        "event_time": _NOW,
        "registration_deadline": _NOW,
        "status": "published",
        "number_of_visitors": 0,
        "changed_at": _NOW,
        "created_at": _NOW,
        "status_changed_at": _NOW,
    }


def _make_page(
    event_ids: list[str], next_url: str | None = None, previous_url: str | None = None
) -> ProviderEventsPageSchema:
    return ProviderEventsPageSchema.model_validate(
        {
            "next": next_url,
            "previous": previous_url,
            "results": [_make_event_payload(event_id) for event_id in event_ids],
        }
    )


@pytest.fixture
def client() -> AsyncMock:
    return AsyncMock(spec=EventsProviderClient)


async def test_paginator_yields_all_events_across_pages(client: AsyncMock) -> None:
    event_id_1, event_id_2, event_id_3 = (str(uuid.uuid4()) for _ in range(3))
    page1 = _make_page(
        [event_id_1, event_id_2],
        next_url="http://provider.test/api/events/?changed_at=2000-01-01&cursor=abc",
    )
    page2 = _make_page([event_id_3], next_url=None)
    client.events.side_effect = [page1, page2]

    events = [event async for event in EventsPaginator(client, changed_at=_CHANGED_AT)]

    assert [str(e.id) for e in events] == [event_id_1, event_id_2, event_id_3]
    assert client.events.await_count == 2


async def test_paginator_stops_when_single_empty_page(client: AsyncMock) -> None:
    client.events.return_value = _make_page([], next_url=None)

    events = [event async for event in EventsPaginator(client, changed_at=_CHANGED_AT)]

    assert events == []
    client.events.assert_awaited_once_with(changed_at=_CHANGED_AT, cursor=None)


async def test_paginator_passes_changed_at_on_every_call(client: AsyncMock) -> None:
    page1 = _make_page(
        [str(uuid.uuid4())],
        next_url="http://provider.test/api/events/?changed_at=2000-01-01&cursor=abc",
    )
    page2 = _make_page([], next_url=None)
    client.events.side_effect = [page1, page2]

    async for _ in EventsPaginator(client, changed_at=_CHANGED_AT):
        pass

    first_call = client.events.await_args_list[0]
    second_call = client.events.await_args_list[1]
    assert first_call.kwargs == {"changed_at": _CHANGED_AT, "cursor": None}
    assert second_call.kwargs == {"changed_at": _CHANGED_AT, "cursor": "abc"}


async def test_paginator_extracts_cursor_from_next_url(client: AsyncMock) -> None:
    page1 = _make_page(
        [str(uuid.uuid4())],
        next_url="http://provider.test/api/events/?changed_at=2000-01-01&cursor=xyz789",
    )
    page2 = _make_page([], next_url=None)
    client.events.side_effect = [page1, page2]

    async for _ in EventsPaginator(client, changed_at=_CHANGED_AT):
        pass

    second_call = client.events.await_args_list[1]
    assert second_call.kwargs["cursor"] == "xyz789"


async def test_paginator_treats_missing_cursor_param_as_none(client: AsyncMock) -> None:
    page1 = _make_page(
        [str(uuid.uuid4())],
        next_url="http://provider.test/api/events/?changed_at=2000-01-01",
    )
    page2 = _make_page([], next_url=None)
    client.events.side_effect = [page1, page2]

    async for _ in EventsPaginator(client, changed_at=_CHANGED_AT):
        pass

    second_call = client.events.await_args_list[1]
    assert second_call.kwargs["cursor"] is None


async def test_paginator_calls_client_exactly_once_per_page(client: AsyncMock) -> None:
    event_ids = [str(uuid.uuid4()) for _ in range(3)]
    page1 = _make_page(event_ids[:2], next_url="http://provider.test/?cursor=abc")
    page2 = _make_page(event_ids[2:], next_url=None)
    client.events.side_effect = [page1, page2]

    paginator = EventsPaginator(client, changed_at=_CHANGED_AT)
    collected = []
    async for event in paginator:
        collected.append(event)
    assert len(collected) == 3
    assert client.events.await_count == 2


async def test_paginator_raises_stop_async_iteration_when_exhausted(
    client: AsyncMock,
) -> None:
    client.events.return_value = _make_page([], next_url=None)

    paginator = EventsPaginator(client, changed_at=_CHANGED_AT)

    with pytest.raises(StopAsyncIteration):
        await paginator.__anext__()
