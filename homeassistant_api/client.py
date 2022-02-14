"""Module for Client class"""

from datetime import datetime
from os.path import join as path
from typing import Any, Coroutine, Dict, List, Optional, Tuple, Union, cast

from .const import DATE_FMT
from .errors import APIConfigurationError, MalformedInputError
from .models import Domain, Entity, Event, Group, JsonModel, State
from .rawapi import RawWrapper


class RawClient(RawWrapper):
    """The class used to interact with all of the api"""

    def __init__(self, *args, **kwargs) -> None:
        """Passes API authentication data to RawWrapper and validates API status"""
        super().__init__(*args, **kwargs)
        self.check_api_running()
        self.check_api_config()

    def __repr__(self) -> str:
        return f'<Client of "{self.api_url[:20]}">'

    # Response processing methods
    def process_services_json(self, json: dict) -> Domain:
        """Constructs Domain and Service models from json data"""
        domain = Domain(cast(str, json.get("domain")), self)
        services = json.get("services")
        if services is None:
            raise ValueError("Missing services atrribute in passed json argument.")
        for service_id, data in services.items():
            domain.add_service(service_id, **data)
        return domain

    def process_state_json(self, json: dict) -> State:
        """Constructs State model from json data"""
        return State(**json)

    def process_event_json(self, json: dict) -> Event:
        """Constructs Event model from json data"""
        return Event(**json, client=self)

    # API information methods
    def api_error_log(self) -> str:
        """Returns the server error log as a string"""
        return cast(str, self.request("error_log"))

    def api_config(self) -> dict:
        """Returns the yaml configuration of homeassistant"""
        return cast(dict, self.request("config"))

    def logbook_entries(
        self,
        filter_entity: Entity = None,
        timestamp: Union[str, datetime] = None,  # Defaults to 1 day before
        end_timestamp: Union[str, datetime] = None,
    ) -> List[dict]:
        params: Dict[str, str] = {}
        if filter_entity is not None:
            params.update(entity=filter_entity.entity_id)
        if end_timestamp is not None:
            if isinstance(end_timestamp, datetime):
                end_timestamp = end_timestamp.strftime(DATE_FMT)
            params.update(end_time=end_timestamp)
        if timestamp is not None:
            if isinstance(timestamp, datetime):
                timestamp = timestamp.strftime(DATE_FMT)
            url = path("logbook", timestamp)
        else:
            url = "logbook"
        return cast(List[dict], self.request(url, params=params))

    def get_history(
        self,
        entities: Tuple[Entity] = None,
        timestamp: datetime = None,  # Defaults to 1 day before. Ref:
        end_timestamp: datetime = None,
        minimal_state_data: bool = False,
        significant_changes_only: bool = False,
    ) -> Union[dict, list, str, Coroutine[Any, Any, Union[dict, list, str]]]:
        params: Dict[str, Optional[str]] = {}

        if entities is not None:
            params["filter_entity_id"] = ",".join([ent.entity_id for ent in entities])
        if end_timestamp is not None:
            params["end_time"] = end_timestamp.strftime(DATE_FMT)
        if minimal_state_data:
            params["minimal_response"] = None
        if significant_changes_only:
            params["significant_changes_only"] = None
        if timestamp is not None:
            if isinstance(timestamp, datetime):
                formatted_timestamp = timestamp.strftime(DATE_FMT)
                url = path("history/period", formatted_timestamp)
            else:
                raise TypeError(f"timestamp needs to be of type {datetime!r}")
        else:
            url = "history/period"
        return self.request(url, params=self.construct_params(params))

    def get_rendered_template(self, template: str) -> str:
        return cast(
            str,
            self.request(
                "template",
                json=dict(template=template),
                return_text=True,
                method="POST",
            ),
        )

    def get_discovery_info(self) -> dict:
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
        else:
            raise ValueError("Server response did not return message attribute")

    def malformed_id(self, entity_id: str) -> bool:
        """Checks whether or not a given entity_id is formatted correctly"""
        checks = [
            " " in entity_id,
            "." not in entity_id,
            "-" in entity_id,
            entity_id.lower() != entity_id,
        ]
        return True in checks

    # Entity methods
    def get_entities(self) -> JsonModel:
        """Fetches all entities from the api"""

        class GroupDict(dict):
            """dict subclass for constructing dynamic default Group models"""

            def __missing__(cls, group_id: str):
                """Allows for dynamic default values in a dictionary"""
                cls[group_id] = Group(group_id, self)
                return cls[group_id]

        entities = GroupDict()
        for state in self.get_states():
            group_id, entity_slug = state.entity_id.split(".")
            entities[group_id].add_entity(entity_slug, state)
        return JsonModel(entities)

    def get_entity(
        self, group_id: str = None, entity_slug: str = None, entity_id: str = None
    ) -> Entity:
        """Returns a Entity model for an entity_id"""
        if group_id is not None and entity_slug is not None:
            state = self.get_state(group=group_id, slug=entity_slug)
        elif entity_id is not None:
            state = self.get_state(entity_id=entity_id)
        else:
            raise ValueError(
                "Neither group and slug or entity_id provided. {help_msg}".format(
                    help_msg="Use keyword arguments to pass entity_id. Or you can pass the entity_group and entity_slug instead"
                )
            )
        group_id, entity_slug = state.entity_id.split(".")
        group = Group(cast(str, group_id), self)
        group.add_entity(cast(str, entity_slug), state)
        return group.get_entity(cast(str, entity_slug))

    # Services and domain methods
    def get_domains(self) -> JsonModel:
        """Fetches all Services from the api"""
        data = self.request("services")
        services = [self.process_services_json(data) for data in cast(List[dict], data)]
        return JsonModel({service.domain_id: service for service in services})

    def trigger_service(self, domain: str, service: str, **service_data) -> List[State]:
        """Tells homeassistant to trigger a service, returns stats changed while being called"""
        data = self.request(
            path("services", domain, service), method="POST", json=service_data
        )
        return [
            self.process_state_json(state_data) for state_data in cast(List[dict], data)
        ]

    # EntityState methods
    def get_state(
        self, entity_id: str = None, group: str = None, slug: str = None
    ) -> State:
        """Fetches the state of the entity specified"""
        if group is not None and slug is not None:
            entity_id = group + "." + slug
        elif entity_id is None:
            raise ValueError("Neither group and slug or entity_id provided.")
        if self.malformed_id(entity_id):
            raise MalformedInputError(f"The entity_id, {entity_id!r}, is malformed")
        data = self.request(path("states", entity_id))
        return self.process_state_json(cast(dict, data))

    def set_state(
        self,
        entity_id: str = None,
        state: str = None,
        group: str = None,
        slug: str = None,
        **payload,
    ) -> State:
        """
        Sets the state of an entity and it does not have to be backed by a real entity.
        Returns the new state afterwards.
        """
        if (group is None or slug is None) and entity_id is None:
            raise ValueError(
                "To use group or slug you need to pass both not just one. "
                "Make sure you are using keyword arguments."
            )
        if group is not None and slug is not None:
            entity_id = group + "." + slug
        elif entity_id is None:
            raise ValueError("Neither group and slug or entity_id provided.")
        if self.malformed_id(entity_id):
            raise MalformedInputError(f"The entity_id, {entity_id!r}, is malformed")
        if state is None:
            raise ValueError('required parameter "state" is missing')
        payload.update(state=state)
        data = self.request(
            path("states", entity_id),
            method="POST",
            json=payload,
        )
        return self.process_state_json(cast(dict, data))

    def get_states(self) -> List[State]:
        """Gets the states of all entitites within homeassistant"""
        data = self.request("states")
        return [
            self.process_state_json(state_data) for state_data in cast(List[dict], data)
        ]

    # Event methods
    def get_events(self) -> JsonModel:
        """Gets the Events that happen within homeassistant"""
        data = self.request("events")
        events = [
            self.process_event_json(event_info) for event_info in cast(List[dict], data)
        ]
        return JsonModel({evt.event_type: evt for evt in events})

    def fire_event(self, event_type: str, **event_data) -> str:
        """Fires a given event_type within homeassistant. Must be an existing event_type."""
        data = self.request(
            path("events", event_type),
            method="POST",
            json=event_data,
        )
        return cast(dict, data).get("message", "No message provided")


class Client(RawClient):
    """
    The base object for interacting with Homeassistant

    :param api_url: The location of the api endpoint. e.g. :code:`http://localhost:8123/api` Required.
    :param token: The refresh or long lived access token to authenticate your requests. Required.
    :param global_request_kwargs: A dictionary or dict-like object of kwargs to pass to :func:`requests.request` or :meth:`aiohttp.ClientSession.request`. Optional.
    """

    def __init__(self, *args, global_request_kwargs: dict = None, **kwargs):
        super().__init__(*args, **kwargs)
        if global_request_kwargs:
            self.global_request_kwargs.update(global_request_kwargs)
