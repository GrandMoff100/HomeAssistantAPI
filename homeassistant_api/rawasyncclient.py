"""Module for interacting with Home Assistant asyncronously."""
import asyncio
import logging
from datetime import datetime
from posixpath import join
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    Union,
    cast,
)

import aiohttp
from aiohttp_client_cache import CachedSession

from .errors import (
    APIConfigurationError,
    BadTemplateError,
    MalformedDataError,
    RequestError,
)
from .models import Domain, Entity, Event, Group, History, LogbookEntry, State
from .processing import Processing
from .rawbaseclient import RawBaseClient

if TYPE_CHECKING:
    from .client import Client
else:
    Client = None  # pylint: disable=invalid-name

logger = logging.getLogger(__name__)


class RawAsyncClient(RawBaseClient):
    """
    The async equivalent of :py:class:`RawClient`

    :param api_url: The location of the api endpoint. e.g. :code:`http://localhost:8123/api` Required.
    :param token: The refresh or long lived access token to authenticate your requests. Required.
    :param global_request_kwargs: A dictionary or dict-like object of kwargs to pass to :func:`requests.request` or :meth:`aiohttp.request`. Optional.
    """  # pylint: disable=line-too-long

    def __init__(
        self,
        *args,
        async_cache_session: Union[
            CachedSession, Literal[False], Literal[None]
        ] = None,  # Explicitly disable cache with async_cache_session=False
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.async_cache_session = (
            async_cache_session if async_cache_session is not None else CachedSession()
        )

    async def __aenter__(self):
        logger.debug(
            "Entering cached async requests session %r", self.async_cache_session
        )
        await self.async_cache_session.__aenter__()
        await self.async_check_api_running()
        return self

    async def __aexit__(self, cls, obj, traceback):
        logger.debug("Exiting async requests session %r", self.async_cache_session)
        await self.async_cache_session.__aexit__(cls, obj, traceback)

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
            if self.async_cache_session:
                return await self.async_response_logic(
                    await self.async_cache_session.request(
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
    async def async_response_logic(response) -> Any:
        """Processes custom mimetype content asyncronously."""
        return await Processing(response=response).process()

    # API information methods
    async def async_get_error_log(self) -> str:
        """Returns the server error log as a string"""
        return cast(str, await self.async_request("error_log"))

    async def async_get_config(self) -> Dict[str, Any]:
        """Returns the yaml configuration of homeassistant"""
        return cast(Dict[str, Any], await self.async_request("config"))

    async def async_get_logbook_entries(
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
        entities: Optional[Tuple[Entity, ...]] = None,
        start_timestamp: Optional[datetime] = None,
        # Defaults to 1 day before. https://developers.home-assistant.io/docs/api/rest/
        end_timestamp: Optional[datetime] = None,
        minimal_state_data: bool = False,
        significant_changes_only: bool = False,
    ) -> AsyncGenerator[History, None]:
        """
        Returns a generator of entity state histories from homeassistant.
        """
        params, url = self.prepare_get_entity_histories_params(
            entities=entities,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            minimal_state_data=minimal_state_data,
            significant_changes_only=significant_changes_only,
        )
        data = await self.async_request(
            url,
            params=self.construct_params(params),
        )
        for states in data:
            yield History.parse_obj({"states": states})

    async def async_get_rendered_template(self, template: str):
        """Renders a given Jinja2 template string with Home Assistant context data."""
        try:
            return await self.async_request(
                "template",
                json=dict(template=template),
                method="POST",
            )
        except RequestError as err:
            raise BadTemplateError(
                "Your template is invalid. "
                "Try debugging it in the developer tools page of homeassistant."
            ) from err

    @staticmethod
    async def async_get_discovery_info() -> Dict[str, Any]:
        """Returns a dictionary of discovery info such as internal_url and version"""
        raise DeprecationWarning(
            "This endpoint has been removed from homeassistant. This function is to be removed in future release."
        )

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
    async def async_get_entities(self) -> Tuple[Group, ...]:
        """Fetches all entities from the api"""
        entities: Dict[str, Group] = {}
        for state in await self.async_get_states():
            group_id, entity_slug = state.entity_id.split(".")
            if group_id not in entities:
                entities[group_id] = Group(group_id=group_id, _client=self)
            entities[group_id].add_entity(entity_slug, state)
        return tuple(entities.values())

    async def async_get_entity(
        self,
        group_id: str = None,
        entity_slug: str = None,
        entity_id: str = None,
    ) -> Optional[Entity]:
        """Returns a Entity model for an :code:`entity_id`"""
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
        group = Group(group_id=group_id, _client=self)
        group.add_entity(entity_slug, state)
        return group.get_entity(entity_slug)

    # Services and domain methods
    async def async_get_domains(self) -> Dict[str, Domain]:
        """Fetches all services from the api"""
        data = await self.async_request("services")
        domains = map(
            lambda json: Domain.from_json(json, _client=cast(Client, self)),
            cast(Tuple[Dict[str, Any], ...], data),
        )
        return {domain.domain_id: domain for domain in domains}

    async def async_get_domain(self, domain_id: str) -> Optional[Domain]:
        """Fetches all services under a particular domain."""
        domains = await self.async_get_domains()
        return domains.get(domain_id)

    async def async_trigger_service(
        self,
        domain: str,
        service: str,
        **service_data: Union[Dict[str, Any], List[Any], str],
    ) -> Tuple[State, ...]:
        """Tells Home Assistant to trigger a service, returns stats changed while being called"""
        data = await self.async_request(
            f"services/{domain}/{service}",
            method="POST",
            json=service_data,
        )
        return tuple(map(State.from_json, cast(List[Dict[Any, Any]], data)))

    # EntityState methods
    async def async_get_state(  # pylint: disable=duplicate-code
        self,
        *,
        entity_id: Optional[str] = None,
        group: Optional[str] = None,
        slug: Optional[str] = None,
    ) -> State:
        """Fetches the state of the entity specified."""
        target_entity_id = self.prepare_entity_id(
            group=group,
            slug=slug,
            entity_id=entity_id,
        )
        data = await self.async_request(join("states", target_entity_id))
        return State.from_json(cast(Dict[Any, Any], data))

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
        return State.from_json(cast(Dict[Any, Any], data))

    async def async_get_states(self) -> Tuple[State, ...]:
        """Gets the states of all entities within homeassistant"""
        data = await self.async_request("states")
        return tuple(map(State.from_json, cast(List[Dict[Any, Any]], data)))

    # Event methods
    async def async_get_events(self) -> Tuple[Event, ...]:
        """Gets the internal events that happen within homeassistant."""
        data = await self.async_request("events")
        if isinstance(data, list):
            return tuple(
                map(
                    lambda json: Event.from_json(json, _client=cast(Client, self)),
                    cast(List[Dict[str, Any]], data),
                )
            )
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

    async def async_get_components(self) -> Tuple[str, ...]:
        """Returns a tuple of all registered components."""
        data = await self.async_request("components")
        return tuple(cast(List[str], data))
