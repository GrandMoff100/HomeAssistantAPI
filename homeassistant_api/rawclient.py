"""Module for all interaction with homeassistant."""

from datetime import datetime
from os.path import join
from typing import Any, Dict, List, Optional, Tuple, Union, cast

import requests

from .const import DATE_FMT
from .errors import APIConfigurationError, RequestError
from .mixins import JsonProcessingMixin
from .models import Domain, Entity, Event, Group, State
from .processing import Processing
from .rawapi import RawWrapper


class RawClient(RawWrapper, JsonProcessingMixin):
    """
    The base object for interacting with Homeassistant

    :param api_url: The location of the api endpoint. e.g. :code:`http://localhost:8123/api` Required.
    :param token: The refresh or long lived access token to authenticate your requests. Required.
    :param global_request_kwargs: Kwargs to pass to :func:`requests.request` or :meth:`aiohttp.ClientSession.request`. Optional.
    """  # pylint: disable=line-too-long

    def __enter__(self):
        self.check_api_running()
        self.check_api_config()
        return self

    def __exit__(self, *args):
        pass

    def request(
        self,
        path,
        method="GET",
        headers: Dict[str, str] = None,
        **kwargs,
    ) -> Union[dict, list, str]:
        """Base method for making requests to the api"""
        try:
            if self.global_request_kwargs is not None:
                kwargs.update(self.global_request_kwargs)
            resp = requests.request(
                method,
                self.endpoint(path),
                headers=self.prepare_headers(headers),
                **kwargs,
            )
        except requests.exceptions.Timeout as err:
            raise RequestError(
                f'Homeassistant did not respond in time (timeout: {kwargs.get("timeout", 300)} sec)'
            ) from err
        return self.response_logic(resp)

    @classmethod
    def response_logic(cls, response: requests.Response) -> Union[dict, list, str]:
        """Processes responses from the api and formats them"""
        processing = Processing(response=response)
        return processing.process()

    # API information methods
    def api_error_log(self) -> str:
        """Returns the server error log as a string."""
        return cast(str, self.request("error_log"))

    def api_config(self) -> Dict[str, Any]:
        """Returns the yaml configuration of homeassistant."""
        return cast(dict, self.request("config"))

    def logbook_entries(
        self,
        filter_entity: Optional[Entity] = None,
        start_timestamp: Optional[
            Union[str, datetime]
        ] = None,  # Defaults to 1 day before
        end_timestamp: Optional[Union[str, datetime]] = None,
    ) -> List[Dict[str, Any]]:
        """Returns a list of logbook entries from homeassistant."""
        params: Dict[str, str] = {}
        if filter_entity is not None:
            params.update(entity=filter_entity.entity_id)
        if end_timestamp is not None:
            if isinstance(end_timestamp, datetime):
                end_timestamp = end_timestamp.strftime(DATE_FMT)
            params.update(end_time=end_timestamp)
        if start_timestamp is not None:
            if isinstance(start_timestamp, datetime):
                formatted_timestamp = start_timestamp.strftime(DATE_FMT)
            url = join("logbook", formatted_timestamp)
        else:
            url = "logbook"
        return cast(List[Dict[str, Any]], self.request(url, params=params))

    def get_history(  # pylint: disable=too-many-arguments
        self,
        entities: Optional[Tuple[Entity, ...]] = None,
        start_timestamp: Optional[datetime] = None,
        # Defaults to 1 day before. https://developers.home-assistant.io/docs/api/rest/
        end_timestamp: Optional[datetime] = None,
        minimal_state_data: bool = False,
        significant_changes_only: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Returns a list of entity state changes from homeassistant.
        (Working on adding a Model for this.)
        """
        params: Dict[str, Optional[str]] = {}

        if entities is not None:
            params["filter_entity_id"] = ",".join([ent.entity_id for ent in entities])
        if end_timestamp is not None:
            params["end_time"] = end_timestamp.strftime(DATE_FMT)
        if minimal_state_data:
            params["minimal_response"] = None
        if significant_changes_only:
            params["significant_changes_only"] = None
        if start_timestamp is not None:
            if isinstance(start_timestamp, datetime):
                formatted_timestamp = start_timestamp.strftime(DATE_FMT)
                url = join("history/period", formatted_timestamp)
            else:
                raise TypeError(f"timestamp needs to be of type {datetime!r}")
        else:
            url = "history/period"
        return cast(
            List[Dict[str, Any]],
            self.request(
                url,
                params=self.construct_params(params),
            ),
        )

    def get_rendered_template(self, template: str) -> str:
        """
        Renders a Jinja2 template with homeassistant context data.
        See https://developers.home-assistant.io/docs/api/rest/.
        """
        return cast(
            str,
            self.request(
                "template",
                json=dict(template=template),
                return_text=True,
                method="POST",
            ),
        )

    def get_discovery_info(self) -> Dict[str, Any]:
        """Returns a dictionary of discovery info such as internal_url and version"""
        res = self.request("discovery_info")
        return cast(dict, res)

    # API check methods
    def check_api_config(self) -> bool:
        """Asks homeassistant to validate its configuration file"""
        res = cast(dict, self.request("config/core/check_config", method="POST"))
        valid = {"valid": True, "invalid": False}.get(res["result"], False)
        if valid is False:
            raise APIConfigurationError(res["errors"])
        return valid

    def check_api_running(self) -> bool:
        """Asks homeassistant if its running"""
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
        """Returns a Entity model for an entity_id"""
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
    def get_domains(self) -> Tuple[Domain, ...]:
        """Fetches all Services from the api"""
        data = self.request("services")
        services = map(
            self.process_services_json,
            cast(Tuple[Dict[str, Any], ...], data),
        )
        return tuple(services)

    def get_domain(self, domain: str) -> Domain:
        """Fetchers all services under a particular domain."""

    def trigger_service(
        self,
        domain: str,
        service: str,
        **service_data,
    ) -> Tuple[State, ...]:
        """Tells homeassistant to trigger a service, returns stats changed while being called"""
        data = self.request(
            join("services", domain, service),
            method="POST",
            json=service_data,
        )
        states = map(self.process_state_json, cast(List[Dict[str, Any]], data))
        return tuple(states)

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
        return self.process_state_json(cast(dict, data))

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
        Sets the state of an entity and it does not have to be backed by a real entity.
        Returns the new state afterwards.
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
        return self.process_state_json(cast(dict, data))

    def get_states(self) -> Tuple[State, ...]:
        """Gets the states of all entities within homeassistant"""
        data = self.request("states")
        states = map(self.process_state_json, cast(List[Dict[str, Any]], data))
        return tuple(states)

    # Event methods
    def get_events(self) -> Tuple[Event, ...]:
        """Gets the Events that happen within homeassistant"""
        data = self.request("events")
        events = map(
            self.process_event_json,
            cast(Tuple[Dict[str, Any], ...], data),
        )
        return tuple(events)

    def fire_event(self, event_type: str, **event_data) -> str:
        """Fires a given event_type within homeassistant. Must be an existing event_type."""
        data = self.request(
            join("events", event_type),
            method="POST",
            json=event_data,
        )
        return cast(dict, data).get("message", "No message provided")
