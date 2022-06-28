"""Module that tests model methods."""
import copy

import pytest

from homeassistant_api import Client
from homeassistant_api.models.states import State


def test_entity_get_entity(cached_client: Client) -> None:
    person_test_suite = cached_client.get_entity(group_id="person", slug="test_suite")
    state = copy.copy(person_test_suite.state)
    person = person_test_suite.group
    assert state.state == person_test_suite.get_state().state
    assert getattr(person, person_test_suite.slug) == person_test_suite
    with pytest.raises(AttributeError):
        assert person.thispersondoesnotexistplease


async def test_async_entity_get_entity(async_cached_client: Client) -> None:
    person_test_suite = await async_cached_client.async_get_entity(
        group_id="person",
        slug="test_suite",
    )
    state = copy.copy(person_test_suite.state)
    person = person_test_suite.group
    assert state.state == (await person_test_suite.async_get_state()).state
    assert getattr(person, person_test_suite.slug) == person_test_suite
    with pytest.raises(AttributeError):
        assert person.thispersondoesnotexistplease


def test_entity_update_state(cached_client: Client) -> None:
    entity = cached_client.get_entity(group_id="sun", slug="red_sun")
    entity.state.state = "In the palm of your hand."
    assert entity.update_state().state == "In the palm of your hand."


async def test_async_entity_update_state(async_cached_client: Client) -> None:
    entity = await async_cached_client.async_get_entity(group_id="sun", slug="red_sun")
    entity.state.state = "In the palm of my hand."
    assert (await entity.async_update_state()).state == "In the palm of my hand."


def test_get_event(cached_client: Client) -> None:
    event = cached_client.get_event("my_favorite_candy_is_mike_and_ikes")
    assert event is None


async def test_async_get_event(async_cached_client: Client) -> None:
    event = await async_cached_client.async_get_event(
        "my_favorite_candy_is_mike_and_ikes"
    )
    assert event is None


def test_fire_event(cached_client: Client) -> None:
    event = cached_client.get_event("core_config_updated")
    assert event.fire() == "Event core_config_updated fired."


async def test_async_fire_event(async_cached_client: Client) -> None:
    event = await async_cached_client.async_get_event("core_config_updated")
    assert await event.async_fire() == "Event core_config_updated fired."


def test_get_domain(cached_client: Client) -> None:
    notify = cached_client.get_domain("notify")
    assert notify.domain_id == "notify"
    with pytest.raises(AttributeError):
        assert notify.thisservicedoesnotexistplease


async def test_async_get_domains(async_cached_client: Client) -> None:
    notify = await async_cached_client.async_get_domain("notify")
    assert notify.domain_id == "notify"
    with pytest.raises(AttributeError):
        assert notify.thisservicedoesnotexistplease


def test_entity_get_history(cached_client: Client) -> None:
    entity = cached_client.get_entity(group_id="sun", slug="red_sun")
    for state in entity.get_history().states:
        assert isinstance(state, State)


async def test_async_entity_get_history(async_cached_client: Client) -> None:
    entity = await async_cached_client.async_get_entity(group_id="sun", slug="red_sun")
    for state in (await entity.async_get_history()).states:
        assert isinstance(state, State)
