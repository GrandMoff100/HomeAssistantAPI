"""Module for interacting with Home Assistant asyncronously."""
import asyncio
from os.path import join
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple, Union, cast

import aiohttp
from aiohttp_client_cache import CachedSession

from ..errors import APIConfigurationError, MalformedDataError, RequestError
from ..mixins import JsonProcessingMixin
from ..models import Domain, Event, History, LogbookEntry, State
from ..processing import Processing
from ..rawapi import RawWrapper
from .models import AsyncEntity, AsyncGroup


class RawAsyncClient(RawWrapper, JsonProcessingMixin):
    """
    The async equivalent of :class:`Client`

    :param api_url: The location of the api endpoint. e.g. :code:`http://localhost:8123/api` Required.
    :param token: The refresh or long lived access token to authenticate your requests. Required.
    :param global_request_kwargs: A dictionary or dict-like object of kwargs to pass to :func:`requests.request` or :meth:`aiohttp.ClientSession.request`. Optional.
    """  # pylint: disable=line-too-long

    _async_session: Optional[CachedSession] = None

    async def __aenter__(self):
        self._async_session = CachedSession(expire_after=30)
        await self._async_session.__aenter__()
        await self.async_check_api_running()
        return self

    async def __aexit__(self, cls, obj, traceback):
        await self._async_session.__aexit__(cls, obj, traceback)

    # Very important request function
    async def async_request(
        self,
        path: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], str]:
        """Base method for making requests to the api"""
        try:
            if self.global_request_kwargs is not None:
                kwargs.update(self.global_request_kwargs)
            if self._async_session is not None:
                return await self.async_response_logic(
                    await self._async_session.request(
                        method,
                        self.endpoint(path),
                        headers=self.prepare_headers(headers),
                        **kwargs,
                    )
                )
            async with aiohttp.request(
                method,
                self.endpoint(path),
                headers=self.prepare_headers(headers),
                **kwargs,
            ) as resp:
                return await self.async_response_logic(resp)
        except asyncio.exceptions.TimeoutError as err:
            raise RequestError(
                f'Home Assistant did not respond in time (timeout: {kwargs.get("timeout", 300)} sec)'
            ) from err

    @staticmethod
    async def async_response_logic(response):
        """Processes custom mimetype content asyncronously."""
        return await Processing(response=response).process()

    # API information methods
    async def async_api_error_log(self) -> str:
        """Returns the server error log as a string"""
        return cast(str, await self.async_request("error_log"))

    async def async_api_config(self) -> Dict[str, Any]:
        """Returns the yaml configuration of homeassistant"""
        return cast(Dict[str, Any], await self.async_request("config"))

    async def async_logbook_entries(
        self,
        *args,
        **kwargs,
    ) -> AsyncGenerator[LogbookEntry, None]:
        """Returns a list of logbook entries from homeassistant."""
        params, url = self.prepare_get_logbook_entry_params(*args, **kwargs)
        data = await self.async_request(url, params=params)
        for entry in data:
            yield LogbookEntry.parse_obj(entry)

    async def async_get_entity_histories(
        self,
        *args,
        **kwargs,
    ) -> AsyncGenerator[History, None]:
        """
        Returns a generator of entity state histories from homeassistant.
        """
        params, url = self.prepare_get_entity_histories_params(*args, **kwargs)
        data = await self.async_request(
            url,
            params=self.construct_params(params),
        )
        for states in data:
            yield History.parse_obj({"states": states})

    async def async_get_rendered_template(self, template: str):
        """Renders a given Jinja2 template string with Home Assistant context data."""
        return await self.async_request(
            "template",
            json=dict(template=template),
            return_text=True,
            method="POST",
        )

    async def async_get_discovery_info(self) -> Dict[str, Any]:
        """Returns a dictionary of discovery info such as internal_url and version"""
        return cast(Dict[str, Any], await self.async_request("discovery_info"))

    # API check methods
    async def async_check_api_config(self) -> bool:
        """Asks Home Assistant to validate its configuration file"""
        res = await self.async_request("config/core/check_config", method="POST")
        res = cast(Dict[Any, Any], res)
        valid = {"valid": True, "invalid": False}.get(
            cast(
                str,
                res["result"],
            ),
            False,
        )
        if valid is False:
            raise APIConfigurationError(res["errors"])
        return valid

    async def async_check_api_running(self) -> bool:
        """Asks Home Assistant if its running"""
        res = cast(Dict[Any, Any], await self.async_request(""))
        if res.get("message", None) == "API running.":
            return True
        raise MalformedDataError("Server response did not return message attribute")

    # Entity methods
    async def async_get_entities(self) -> Tuple[AsyncGroup, ...]:
        """Fetches all entities from the api"""
        entities: Dict[str, AsyncGroup] = {}
        for state in await self.async_get_states():
            group_id, entity_slug = state.entity_id.split(".")
            if group_id not in entities:
                entities[group_id] = AsyncGroup(group_id=group_id, client=self)
            entities[group_id].add_entity(entity_slug, state)
        return tuple(entities.values())

    async def async_get_entity(
        self,
        group_id: str = None,
        entity_slug: str = None,
        entity_id: str = None,
    ) -> Optional[AsyncEntity]:
        """Returns a Entity model for an entity_id"""
        if group_id is not None and entity_slug is not None:
            state = await self.async_get_state(group=group_id, slug=entity_slug)
        elif entity_id is not None:
            state = await self.async_get_state(entity_id=entity_id)
        else:
            help_msg = (
                "Use keyword arguments to pass entity_id. "
                "Or you can pass the entity_group and entity_slug instead."
            )
            raise ValueError(
                f"Neither group and slug or entity_id provided. {help_msg}"
            )
        group_id, entity_slug = state.entity_id.split(".")
        group = AsyncGroup(group_id=cast(str, group_id), client=self)
        group.add_entity(cast(str, entity_slug), state)
        return group.get_entity(cast(str, entity_slug))

    # Services and domain methods
    async def async_get_domains(self) -> Tuple[Domain, ...]:
        """Fetches all Services from the api"""
        data = await self.async_request("services")
        services = map(
            self.process_services_json,
            cast(Tuple[Dict[str, Any], ...], data),
        )
        return tuple(services)

    async def async_trigger_service(
        self,
        domain: str,
        service: str,
        **service_data,
    ) -> List[State]:
        """Tells Home Assistant to trigger a service, returns stats changed while being called"""
        data = await self.async_request(
            join("services", domain, service),
            method="POST",
            json=service_data,
        )
        return [
            self.process_state_json(state_data)
            for state_data in cast(List[Dict[Any, Any]], data)
        ]

    # EntityState methods
    async def async_get_state(  # pylint: disable=duplicate-code
        self,
        *,
        entity_id: Optional[str] = None,
        group: Optional[str] = None,
        slug: Optional[str] = None,
    ) -> State:
        """Fetches the state of the entity specified"""
        target_entity_id = self.prepare_entity_id(
            group=group,
            slug=slug,
            entity_id=entity_id,
        )
        data = await self.async_request(join("states", target_entity_id))
        return self.process_state_json(cast(Dict[Any, Any], data))

    async def async_set_state(  # pylint: disable=duplicate-code
        self,
        state: str,
        *,
        entity_id: Optional[str] = None,
        group: Optional[str] = None,
        slug: Optional[str] = None,
        **payload,
    ) -> State:
        """Sets the state of the entity given (does not have to be a real entity) and returns the updated state"""
        target_entity_id = self.prepare_entity_id(
            group=group,
            slug=slug,
            entity_id=entity_id,
        )
        payload.update(state=state)
        data = await self.async_request(
            join("states", target_entity_id),
            method="POST",
            json=payload,
        )
        return self.process_state_json(cast(Dict[Any, Any], data))

    async def async_get_states(self) -> List[State]:
        """Gets the states of all entities within homeassistant"""
        data = await self.async_request("states")
        return [
            self.process_state_json(state_data)
            for state_data in cast(List[Dict[Any, Any]], data)
        ]

    # Event methods
    async def async_get_events(self) -> Tuple[Event, ...]:
        """Gets the Events that happen within homeassistant"""
        data = await self.async_request("events")
        if not isinstance(data, list):
            events = map(
                self.process_event_json,
                cast(List[Dict[Any, Any]], data),
            )
            return tuple(events)
        raise TypeError("Received JSON data is not a list of events.")

    async def async_fire_event(self, event_type: str, **event_data) -> str:
        """Fires a given event_type within homeassistant. Must be an existing event_type."""
        data = await self.async_request(
            join("events", event_type),
            method="POST",
            json=event_data,
        )
        if not isinstance(data, dict):
            raise TypeError(
                f"Invalid return type from API. Expected {dict!r} got {type(data)!r}"
            )
        return data.get("message", "No message provided")
