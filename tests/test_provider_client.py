import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from app.clients.events_provider import EventsProviderClient

FAKE_BASE_URL = "http://events-provider.local"
FAKE_API_KEY = "test-api-key-000"

_NOW = datetime(2026, 9, 5, tzinfo=UTC).isoformat()


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


def _make_event_payload(event_id: str | None = None) -> dict:
    return {
        "id": event_id or str(uuid.uuid4()),
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


def _make_response(json_body: dict | None = None, status_code: int = 200) -> MagicMock:
    response = MagicMock(spec=httpx.Response)
    response.status_code = status_code
    response.json.return_value = json_body or {}

    if status_code >= 400:
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "error", request=MagicMock(), response=response
        )
    else:
        response.raise_for_status.side_effect = None

    return response


@pytest.fixture
def client() -> EventsProviderClient:
    return EventsProviderClient(
        base_url=FAKE_BASE_URL, api_key=FAKE_API_KEY, timeout=5.0
    )


def test_client_sets_api_key_header(client: EventsProviderClient) -> None:
    assert client._client.headers["x-api-key"] == FAKE_API_KEY


def test_client_without_api_key_omits_header() -> None:
    anon_client = EventsProviderClient(base_url=FAKE_BASE_URL)

    assert "x-api-key" not in anon_client._client.headers


def test_client_strips_trailing_slash_from_base_url() -> None:
    trailing_slash_client = EventsProviderClient(base_url=f"{FAKE_BASE_URL}/")

    assert trailing_slash_client._client.base_url == httpx.URL(FAKE_BASE_URL)


async def test_events_sends_changed_at_param(client: EventsProviderClient) -> None:
    event_id = str(uuid.uuid4())
    page = {"next": None, "previous": None, "results": [_make_event_payload(event_id)]}
    client._client.get = AsyncMock(return_value=_make_response(page))

    result = await client.events(changed_at="2000-01-01")

    client._client.get.assert_awaited_once_with(
        url="/api/events/", params={"changed_at": "2000-01-01"}
    )
    assert str(result.results[0].id) == event_id


async def test_events_includes_cursor_when_provided(
    client: EventsProviderClient,
) -> None:
    page = {"next": None, "previous": None, "results": []}
    client._client.get = AsyncMock(return_value=_make_response(page))

    await client.events(changed_at="2000-01-01", cursor="cursor-abc")

    _, kwargs = client._client.get.await_args
    assert kwargs["params"] == {"changed_at": "2000-01-01", "cursor": "cursor-abc"}


async def test_events_omits_cursor_when_not_provided(
    client: EventsProviderClient,
) -> None:
    page = {"next": None, "previous": None, "results": []}
    client._client.get = AsyncMock(return_value=_make_response(page))

    await client.events(changed_at="2000-01-01")

    _, kwargs = client._client.get.await_args
    assert "cursor" not in kwargs["params"]


async def test_events_raises_on_http_error(client: EventsProviderClient) -> None:
    client._client.get = AsyncMock(return_value=_make_response(status_code=500))

    with pytest.raises(httpx.HTTPStatusError):
        await client.events()


async def test_get_seats_calls_correct_url(client: EventsProviderClient) -> None:
    body = {"seats": ["A1", "A2"]}
    client._client.get = AsyncMock(return_value=_make_response(body))

    result = await client.get_seats("event-1")

    client._client.get.assert_awaited_once_with(url="/api/events/event-1/seats/")
    assert result.seats == ["A1", "A2"]


async def test_get_seats_raises_on_http_error(client: EventsProviderClient) -> None:
    client._client.get = AsyncMock(return_value=_make_response(status_code=404))

    with pytest.raises(httpx.HTTPStatusError):
        await client.get_seats("missing-event")


async def test_register_sends_expected_payload(client: EventsProviderClient) -> None:
    ticket_id = str(uuid.uuid4())
    body = {"ticket_id": ticket_id}
    client._client.post = AsyncMock(return_value=_make_response(body))

    result = await client.register(
        event_id="event-1",
        first_name="Anna",
        last_name="Karlsson",
        email="anna@example.com",
        seat="B12",
    )

    client._client.post.assert_awaited_once_with(
        url="/api/events/event-1/register/",
        json={
            "first_name": "Anna",
            "last_name": "Karlsson",
            "email": "anna@example.com",
            "seat": "B12",
        },
    )
    assert str(result.ticket_id) == ticket_id


async def test_register_raises_on_http_error(client: EventsProviderClient) -> None:
    client._client.post = AsyncMock(return_value=_make_response(status_code=400))

    with pytest.raises(httpx.HTTPStatusError):
        await client.register(
            event_id="event-1",
            first_name="Anna",
            last_name="Karlsson",
            email="anna@example.com",
            seat="B12",
        )


async def test_unregister_sends_ticket_id_via_delete(
    client: EventsProviderClient,
) -> None:
    body = {"success": True}
    client._client.request = AsyncMock(return_value=_make_response(body))

    result = await client.unregister(event_id="event-1", ticket_id="ticket-1")

    client._client.request.assert_awaited_once_with(
        method="DELETE",
        url="/api/events/event-1/unregister/",
        json={"ticket_id": "ticket-1"},
    )
    assert result.success is True


async def test_unregister_raises_on_http_error(client: EventsProviderClient) -> None:
    client._client.request = AsyncMock(return_value=_make_response(status_code=404))

    with pytest.raises(httpx.HTTPStatusError):
        await client.unregister(event_id="event-1", ticket_id="missing-ticket")


async def test_aclose_closes_underlying_httpx_client(
    client: EventsProviderClient,
) -> None:
    client._client.aclose = AsyncMock()

    await client.aclose()

    client._client.aclose.assert_awaited_once()


async def test_async_context_manager_closes_client_on_exit() -> None:
    async with EventsProviderClient(base_url=FAKE_BASE_URL) as ctx_client:
        ctx_client._client.aclose = AsyncMock()
        aclose_mock = ctx_client._client.aclose

    aclose_mock.assert_awaited_once()
