# pylint: disable=redefined-outer-name
import os
from typing import Generator

import pytest
import pytest_asyncio

from homeassistant_api import Client
from homeassistant_api.models.events import Event
from homeassistant_api.models.states import State


@pytest.fixture(scope="function")
def cached_client() -> Generator[Client, None, None]:
    """Initializes the Client and enters a cached session."""
    with Client(
        os.environ["HOMEASSISTANTAPI_URL"], os.environ["HOMEASSISTANTAPI_TOKEN"]
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def async_cached_client() -> Generator[Client, None, None]:
    """Initializes the Client and enters an async cached session."""
    async with Client(
        os.environ["HOMEASSISTANTAPI_URL"], os.environ["HOMEASSISTANTAPI_TOKEN"]
    ) as client:
        yield client


def test_get_error_log(cached_client: Client) -> None:
    """Tests the `GET /api/error_log` endpoint."""
    assert cached_client.get_error_log()


async def test_async_get_error_log(async_cached_client: Client) -> None:
    """Tests the `GET /api/error_log` endpoint."""
    assert await async_cached_client.async_get_error_log()


def test_get_config(cached_client: Client) -> None:
    """Tests the `GET /api/config` endpoint."""
    assert cached_client.get_config().get("state") == "RUNNING"


async def test_async_get_config(async_cached_client: Client) -> None:
    """Tests the `GET /api/config` endpoint."""
    assert (await async_cached_client.async_get_config()).get("state") == "RUNNING"


def test_get_logbook_entries(cached_client: Client) -> None:
    """Tests the `GET /api/logbook/<timestamp>` endpoint."""
    for entry in cached_client.get_logbook_entries():
        assert entry


async def test_async_get_logbook_entries(async_cached_client: Client) -> None:
    """Tests the `GET /api/logbook/<timestamp>` endpoint."""
    async for entry in async_cached_client.async_get_logbook_entries():
        assert entry


def test_get_entity(cached_client: Client) -> None:
    """Tests the `GET /api/states/<entity_id>` endpoint."""
    assert cached_client.get_entity(entity_id="sun.sun")


async def test_async_get_entity(async_cached_client: Client) -> None:
    """Tests the `GET /api/states/<entity_id>` endpoint."""
    assert await async_cached_client.async_get_entity(entity_id="sun.sun")


def test_get_entity_histories(cached_client: Client) -> None:
    """Tests the `GET /api/history/period/<timestamp>` endpoint."""
    for history in cached_client.get_entity_histories(
        [cached_client.get_entity(entity_id="sun.sun")]
    ):
        for state in history.states:
            assert isinstance(state, State)


async def test_async_get_entity_histories(async_cached_client: Client) -> None:
    """Tests the `GET /api/history/period/<timestamp>` endpoint."""
    async for history in async_cached_client.async_get_entity_histories(
        [await async_cached_client.async_get_entity(entity_id="sun.sun")]
    ):
        for state in history.states:
            assert isinstance(state, State)


def test_get_rendered_template(cached_client: Client) -> None:
    """Tests the `POST /api/template` endpoint."""
    rendered_template = cached_client.get_rendered_template(
        'The sun is {{ states("sun.sun").replace("_", " the ") }}.'
    )
    assert rendered_template in {
        "The sun is above the horizon.",
        "The sun is below the horizon.",
    }


async def test_async_get_rendered_template(async_cached_client: Client) -> None:
    """Tests the `POST /api/template` endpoint."""
    rendered_template = await async_cached_client.async_get_rendered_template(
        'The sun is {{ states("sun.sun").replace("_", " the ") }}.'
    )
    assert rendered_template in {
        "The sun is above the horizon.",
        "The sun is below the horizon.",
    }


def test_check_api_config(cached_client: Client) -> None:
    """Tests the `POST /api/config/core/check_config` endpoint."""
    assert cached_client.check_api_config()


async def test_async_check_api_config(async_cached_client: Client) -> None:
    """Tests the `POST /api/config/core/check_config` endpoint."""
    assert await async_cached_client.async_check_api_config()


def test_get_entities(cached_client: Client) -> None:
    """Tests the `GET /api/states` endpoint."""
    entities = cached_client.get_entities()
    assert "sun" in entities


async def test_async_get_entities(async_cached_client: Client) -> None:
    """Tests the `GET /api/states` endpoint."""
    entities = await async_cached_client.async_get_entities()
    assert any(group.group_id == "sun" for group in entities)


def test_get_domains(cached_client: Client) -> None:
    """Tests the `GET /api/services` endpoint."""
    domains = cached_client.get_domains()
    assert "homeassistant" in domains


async def test_async_get_domains(async_cached_client: Client) -> None:
    """Tests the `GET /api/services` endpoint."""
    domains = await async_cached_client.async_get_domains()
    assert "homeassistant" in domains


def test_get_domain(cached_client: Client) -> None:
    """Tests the `GET /api/services` endpoint."""
    domain = cached_client.get_domain("homeassistant")
    assert domain.services


async def test_async_get_domain(async_cached_client: Client) -> None:
    """Tests the `GET /api/services` endpoint."""
    domain = await async_cached_client.async_get_domain("homeassistant")
    assert domain.services


def test_trigger_service(cached_client: Client) -> None:
    """Tests the `POST /api/services/<domain>/<service>` endpoint."""
    notify = cached_client.get_domain("notify")
    resp = notify.persistent_notification(
        message="Your API Test Suite just said hello!",
        title="Test Suite Notifcation",
    )
    assert isinstance(resp, tuple)


async def test_async_trigger_service(async_cached_client: Client) -> None:
    """Tests the `POST /api/services/<domain>/<service>` endpoint."""
    notify = await async_cached_client.async_get_domain("notify")
    resp = await notify.persistent_notification.async_trigger(
        message="Your API Test Suite just said hello!",
        title="Test Suite Notifcation (Async)",
    )
    assert isinstance(resp, tuple)


def test_get_states(cached_client: Client) -> None:
    """Tests the `GET /api/states` endpoint."""
    states = cached_client.get_states()
    for state in states:
        assert isinstance(state, State)


async def test_async_get_states(async_cached_client: Client) -> None:
    """Tests the `GET /api/states` endpoint."""
    states = await async_cached_client.async_get_states()
    for state in states:
        assert isinstance(state, State)


def test_get_state(cached_client: Client) -> None:
    """Tests the `GET /api/states/<entity_id>` endpoint."""
    state = cached_client.get_state(entity_id="sun.sun")
    assert state.state in {"above_horizon", "below_horizon"}


async def test_async_get_state(async_cached_client: Client) -> None:
    """Tests the `GET /api/states/<entity_id>` endpoint."""
    state = await async_cached_client.async_get_state(entity_id="sun.sun")
    assert state.state in {"above_horizon", "below_horizon"}


def test_set_state(cached_client: Client) -> None:
    """Tests the `POST /api/states/<entity_id>` endpoint."""
    state = cached_client.set_state("beyond_our_solar_system", entity_id="sun.red_sun")
    assert state.state == "beyond_our_solar_system"


async def test_async_set_state(async_cached_client: Client) -> None:
    """Tests the `POST /api/states/<entity_id>` endpoint."""
    state = await async_cached_client.async_set_state(
        "beyond_our_solar_system", entity_id="sun.red_sun"
    )
    assert state.state == "beyond_our_solar_system"


def test_get_events(cached_client: Client) -> None:
    """Tests the `GET /api/events` endpoint."""
    events = cached_client.get_events()
    for event in events:
        assert isinstance(event, Event)


async def test_async_get_events(async_cached_client: Client) -> None:
    """Tests the `GET /api/events` endpoint."""
    events = await async_cached_client.async_get_events()
    for event in events:
        assert isinstance(event, Event)


def test_fire_event(cached_client: Client) -> None:
    """Tests the `POST /api/events/<event_type>` endpoint."""
    data = cached_client.fire_event("my_new_event", parameter="123")
    assert data == "Event my_new_event fired."


async def test_async_fire_event(async_cached_client: Client) -> None:
    """Tests the `POST /api/events/<event_type>` endpoint."""
    data = await async_cached_client.async_fire_event("my_new_event", parameter="123")
    assert data == "Event my_new_event fired."
