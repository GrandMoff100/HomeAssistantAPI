"""Module for all interaction with homeassistant."""

import logging
from datetime import datetime
from posixpath import join
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generator,
    List,
    Literal,
    Optional,
    Tuple,
    Union,
    cast,
)

import requests
from requests_cache import CachedSession

from .errors import APIConfigurationError, BadTemplateError, RequestError
from .models import Domain, Entity, Event, Group, History, LogbookEntry, State
from .processing import Processing
from .rawbaseclient import RawBaseClient

if TYPE_CHECKING:
    from .client import Client
else:
    Client = None  # pylint: disable=invalid-name


logger = logging.getLogger(__name__)


class RawClient(RawBaseClient):
    """
    The base object for interacting with Homeassistant

    :param api_url: The location of the api endpoint. e.g. :code:`http://localhost:8123/api` Required.
    :param token: The refresh or long lived access token to authenticate your requests. Required.
    :param global_request_kwargs: Kwargs to pass to :func:`requests.request` or :meth:`aiohttp.ClientSession.request`. Optional.
    """  # pylint: disable=line-too-long

    def __init__(
        self,
        *args,
        cache_session: Union[
            CachedSession, Literal[False], Literal[None]
        ] = None,  # Explicitly disable cache with cache_session=False
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.cache_session = (
            cache_session if cache_session is not None else CachedSession()
        )

    def __enter__(self):
        logger.debug("Entering cached requests session %r.", self.cache_session)
        self.cache_session.__enter__()
        self.check_api_running()
        self.check_api_config()
        return self

    def __exit__(self, *args):
        logger.debug("Exiting requests session %r", self.cache_session)
        self.cache_session.__exit__(*args)

    def request(
        self,
        path,
        method="GET",
        headers: Dict[str, str] = None,
        **kwargs,
    ) -> Union[Dict[str, Any], list, str]:
        """Base method for making requests to the api"""
        try:
            if self.global_request_kwargs is not None:
                kwargs.update(self.global_request_kwargs)
            logger.debug("%s request to %s", method, self.endpoint(path))
            if self.cache_session:
                resp = self.cache_session.request(
                    method,
                    self.endpoint(path),
                    headers=self.prepare_headers(headers),
                    **kwargs,
                )
            else:
                resp = requests.request(
                    method,
                    self.endpoint(path),
                    headers=self.prepare_headers(headers),
                    **kwargs,
                )
        except requests.exceptions.Timeout as err:
            raise RequestError(
                f'Home Assistant did not respond in time (timeout: {kwargs.get("timeout", 300)} sec)'
            ) from err
        return self.response_logic(resp)

    @classmethod
    def response_logic(cls, response: requests.Response) -> Union[dict, list, str]:
        """Processes responses from the API and formats them"""
        return Processing(response=response).process()

    # API information methods
    def get_error_log(self) -> str:
        """Returns the server error log as a string."""
        return cast(str, self.request("error_log"))

    def get_config(self) -> Dict[str, Any]:
        """Returns the yaml configuration of homeassistant."""
        return cast(Dict[str, Any], self.request("config"))

    def get_logbook_entries(
        self,
        *args,
        **kwargs,
    ) -> Generator[LogbookEntry, None, None]:
        """Returns a list of logbook entries from homeassistant."""
        params, url = self.prepare_get_logbook_entry_params(*args, **kwargs)
        data = self.request(url, params=params)
        for entry in data:
            yield LogbookEntry.parse_obj(entry)

    def get_entity_histories(
        self,
        entities: Optional[Tuple[Entity, ...]] = None,
        start_timestamp: Optional[datetime] = None,
        # Defaults to 1 day before. https://developers.home-assistant.io/docs/api/rest/
        end_timestamp: Optional[datetime] = None,
        minimal_state_data: bool = False,
        significant_changes_only: bool = False,
    ) -> Generator[History, None, None]:
        """
        Yields entity state histories. See docs on the `History` model.
        """
        params, url = self.prepare_get_entity_histories_params(
            entities=entities,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            minimal_state_data=minimal_state_data,
            significant_changes_only=significant_changes_only,
        )
        data = self.request(
            url,
            params=self.construct_params(params),
        )
        for states in data:
            yield History.parse_obj({"states": states})

    def get_rendered_template(self, template: str) -> str:
        """
        Renders a Jinja2 template with Home Assistant context data.
        See https://www.home-assistant.io/docs/configuration/templating.
        """
        try:
            return cast(
                str,
                self.request(
                    "template",
                    json=dict(template=template),
                    method="POST",
                ),
            )
        except RequestError as err:
            raise BadTemplateError(
                "Your template is invalid. "
                "Try debugging it in the developer tools page of homeassistant."
            ) from err

    @staticmethod
    def get_discovery_info() -> Dict[str, Any]:
        """Returns a dictionary of discovery info such as internal_url and version"""
        raise DeprecationWarning(
            "This endpoint has been removed from homeassistant. This function is to be removed in future release."
        )

    # API check methods
    def check_api_config(self) -> bool:
        """Asks Home Assistant to validate its configuration file."""
        res = cast(dict, self.request("config/core/check_config", method="POST"))
        valid = {"valid": True, "invalid": False}.get(res["result"], False)
        if valid is False:
            raise APIConfigurationError(res["errors"])
        return valid

    def check_api_running(self) -> bool:
        """Asks Home Assistant if it is running."""
        res = self.request("")
        if cast(dict, res).get("message", None) == "API running.":
            return True
        raise ValueError("Server response did not return message attribute")

    # Entity methods
    def get_entities(self) -> Dict[str, Group]:
        """Fetches all entities from the api"""
        entities: Dict[str, Group] = {}
        for state in self.get_states():
            group_id, entity_slug = state.entity_id.split(".")
            if group_id not in entities:
                entities[group_id] = Group(group_id=cast(str, group_id), client=self)
            entities[group_id].add_entity(entity_slug, state)
        return entities

    def get_entity(
        self,
        group_id: str = None,
        entity_slug: str = None,
        entity_id: str = None,
    ) -> Optional[Entity]:
        """Returns an :py:class:`Entity` model for an :code:`entity_id`"""
        if group_id is not None and entity_slug is not None:
            state = self.get_state(group=group_id, slug=entity_slug)
        elif entity_id is not None:
            state = self.get_state(entity_id=entity_id)
        else:
            help_msg = (
                "Use keyword arguments to pass entity_id. "
                "Or you can pass the entity_group and entity_slug instead"
            )
            raise ValueError(
                f"Neither group and slug or entity_id provided. {help_msg}"
            )
        group_id, entity_slug = state.entity_id.split(".")
        group = Group(group_id=cast(str, group_id), client=self)
        group.add_entity(cast(str, entity_slug), state)
        return group.get_entity(cast(str, entity_slug))

    # Services and domain methods
    def get_domains(self) -> Dict[str, Domain]:
        """Fetches all :py:class:`Service`s from the API."""
        data = self.request("services")
        domains = map(
            lambda json: Domain.from_json(json, client=cast(Client, self)),
            cast(Tuple[Dict[str, Any], ...], data),
        )
        return {domain.domain_id: domain for domain in domains}

    def get_domain(self, domain_id: str) -> Optional[Domain]:
        """Fetches all services under a particular domain."""
        return self.get_domains().get(domain_id)

    def trigger_service(
        self,
        domain: str,
        service: str,
        **service_data,
    ) -> Tuple[State, ...]:
        """Tells Home Assistant to trigger a service, returns all states changed while in the process of being called."""
        data = self.request(
            join("services", domain, service),
            method="POST",
            json=service_data,
        )
        return tuple(map(State.from_json, cast(List[Dict[str, Any]], data)))

    # EntityState methods
    def get_state(  # pylint: disable=duplicate-code
        self,
        *,
        entity_id: Optional[str] = None,
        group: Optional[str] = None,
        slug: Optional[str] = None,
    ) -> State:
        """Fetches the state of the entity specified"""
        entity_id = self.prepare_entity_id(
            group=group,
            slug=slug,
            entity_id=entity_id,
        )
        data = self.request(join("states", entity_id))
        return State.from_json(cast(Dict[str, Any], data))

    def set_state(  # pylint: disable=duplicate-code
        self,
        state: str,
        *,
        entity_id: Optional[str] = None,
        group: Optional[str] = None,
        slug: Optional[str] = None,
        **payload,
    ) -> State:
        """
        This method sets the representation of a device within Home Assistant and will not communicate with the actual device.
        To communicate with the device, use :py:meth:`Service.trigger` or :py:meth:`Service.async_trigger`
        """
        entity_id = self.prepare_entity_id(
            group=group,
            slug=slug,
            entity_id=entity_id,
        )
        payload.update(state=state)
        data = self.request(
            join("states", entity_id),
            method="POST",
            json=payload,
        )
        return State.from_json(cast(dict, data))

    def get_states(self) -> Tuple[State, ...]:
        """Gets the states of all entities within homeassistant"""
        data = self.request("states")
        states = map(State.from_json, cast(List[Dict[str, Any]], data))
        return tuple(states)

    # Event methods
    def get_events(self) -> Tuple[Event, ...]:
        """Gets the Events that happen within homeassistant"""
        data = self.request("events")
        if isinstance(data, list):
            return tuple(
                map(
                    lambda json: Event.from_json(json, client=cast(Client, self)),
                    cast(List[Dict[str, Any]], data),
                )
            )
        raise TypeError("Received JSON data is not a list of events.")

    def fire_event(self, event_type: str, **event_data) -> Optional[str]:
        """Fires a given event_type within homeassistant. Must be an existing event_type."""
        data = self.request(
            join("events", event_type),
            method="POST",
            json=event_data,
        )
        return cast(dict, data).get("message")

    def get_components(self) -> Tuple[str, ...]:
        """Returns a tuple of all registered components."""
        return tuple(self.request("components"))
