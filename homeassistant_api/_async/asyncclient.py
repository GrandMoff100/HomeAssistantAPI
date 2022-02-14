import asyncio
from datetime import datetime
from os.path import join as path
from typing import Any, Dict, List, Tuple, Union, cast

import aiohttp

from ..client import RawWrapper
from ..errors import APIConfigurationError, MalformedDataError, RequestError
from ..models import JsonModel, State
from ..processing import Processing
from .models import AsyncDomain, AsyncEntity, AsyncEvent, AsyncGroup


class AsyncClient(RawWrapper):
    """
    The async equivalent of :class:`Client`

    :param api_url: The location of the api endpoint. e.g. :code:`http://localhost:8123/api` Required.
    :param token: The refresh or long lived access token to authenticate your requests. Required.
    :param global_request_kwargs: A dictionary or dict-like object of kwargs to pass to :func:`requests.request` or :meth:`aiohttp.ClientSession.request`. Optional.
    """

    def __init__(self, *args, global_request_kwargs: dict = None, **kwargs):
        super().__init__(*args, **kwargs)
        if global_request_kwargs:
            self.global_request_kwargs.update(global_request_kwargs)

    def __repr__(self) -> str:
        return f'<AsyncClient of "{self.api_url[:20]}">'

    async def __aenter__(self):
        await self.check_api_running()
        await self.check_api_config()
        return self

    async def __aexit__(self, cls, obj, tb):
        pass

    # Very important request function
    async def async_request(
        self,
        path,
        method="GET",
        headers: dict = None,
        **kwargs,
    ) -> Union[dict, list, str]:
        """Base method for making requests to the api"""
        if headers is None:
            headers = {}
        if isinstance(headers, dict):
            headers.update(self._headers)
        else:
            raise ValueError(
                f"headers must be dict or dict subclass, not type {type(headers).__name__!r}"
            )
        async with aiohttp.ClientSession() as session:
            try:
                resp = await session.request(
                    method,
                    self.endpoint(path),
                    headers=headers,
                    **kwargs,
                    **self.global_request_kwargs,
                )
            except asyncio.exceptions.TimeoutError:
                raise RequestError(
                    f'Homeassistant did not respond in time (timeout: {kwargs.get("timeout", 300)} sec)'
                )
        return await self.response_logic(resp)

    async def response_logic(self, response):
        return await Processing(response).process(_async=True)

    # Response processing methods
    def process_services_json(self, json: dict) -> AsyncDomain:
        """Constructs Domain and Service models from json data"""
        domain = AsyncDomain(cast(str, json.get("domain")), self)
        services = json.get("services")
        if services is None:
            raise ValueError("Missing services atrribute in passed json argument.")
        for service_id, data in services.items():
            domain.add_service(service_id, **data)
        return domain

    def process_state_json(self, json: dict) -> State:
        """Constructs State model from json data"""
        return State(**json)

    def process_event_json(self, json: dict) -> AsyncEvent:
        """Constructs Event model from json data"""
        return AsyncEvent(**json, client=self)

    # API information methods
    async def api_error_log(self) -> str:
        """Returns the server error log as a string"""
        return cast(str, await self.async_request("error_log", return_text=True))

    async def api_config(self) -> dict:
        """Returns the yaml configuration of homeassistant"""
        return cast(dict, await self.async_request("config"))

    async def logbook_entries(
        self,
        filter_entity: AsyncEntity = None,
        timestamp: Union[str, datetime] = None,  # Defaults to 1 day before
        end_timestamp: Union[str, datetime] = None,
    ) -> dict:
        # TODO: Implement async logbook_entries
        pass

    async def get_history(
        self,
        entities: Tuple[AsyncEntity] = None,
        timestamp: datetime = None,  # Defaults to 1 day before
        end_timestamp: datetime = None,
        minimal_state_data=False,
        significant_changes_only=False,
    ) -> Union[dict, list, str]:
        # TODO: Implement async get_history
        pass

    async def get_rendered_template(self, template: str):
        return await self.async_request(
            "template",
            json=dict(template=template),
            return_text=True,
            method="POST",
        )

    async def get_discovery_info(self) -> dict:
        """Returns a dictionary of discovery info such as internal_url and version"""
        return cast(dict, await self.async_request("discovery_info"))

    # API check methods
    async def check_api_config(self) -> bool:
        """Asks homeassistant to validate its configuration file"""
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

    async def check_api_running(self) -> bool:
        """Asks homeassistant if its running"""
        res = cast(Dict[Any, Any], await self.async_request(""))
        if res.get("message", None) == "API running.":
            return True
        else:
            raise MalformedDataError("Server response did not return message attribute")

    async def malformed_id(self, entity_id: str) -> bool:
        """Checks whether or not a given entity_id is formatted correctly"""
        checks = [
            " " in entity_id,
            "." not in entity_id,
            "-" in entity_id,
            entity_id.lower() == entity_id,
        ]
        return True in checks

    # Entity methods
    async def get_entities(self) -> JsonModel:
        """Fetches all entities from the api"""

        class GroupDict(dict):
            """dict subclass for constructing dynamic default Group models"""

            def __missing__(cls, group_id: str):
                """Allows for dynamic default values in a dictionary"""
                cls[group_id] = AsyncGroup(group_id, self)
                return cls[group_id]

        entities = GroupDict()
        for state in await self.get_states():
            group_id, entity_slug = state.entity_id.split(".")
            entities[group_id].add_entity(entity_slug, state)
        return JsonModel(entities)

    async def get_entity(
        self, group_id: str = None, entity_slug: str = None, entity_id: str = None
    ) -> AsyncEntity:
        """Returns a Entity model for an entity_id"""
        if group_id is not None and entity_slug is not None:
            state = await self.get_state(group=group_id, slug=entity_slug)
        elif entity_id is not None:
            state = await self.get_state(entity_id=entity_id)
        else:
            raise ValueError(
                "Neither group and slug or entity_id provided. {help_msg}".format(
                    help_msg="Use keyword arguments to pass entity_id. Or you can pass the entity_group and entity_slug "
                    "instead "
                )
            )
        group_id, entity_slug = state.entity_id.split(".")
        group = AsyncGroup(cast(str, group_id), self)
        group.add_entity(cast(str, entity_slug), state)
        return group.get_entity(cast(str, entity_slug))

    # Services and domain methods
    async def get_domains(self) -> JsonModel:
        """Fetches all Services from the api"""
        services = await self.async_request("services")
        services = [
            self.process_services_json(data)
            for data in cast(List[Dict[Any, Any]], services)
        ]
        services = {service.domain_id: service for service in services}
        return JsonModel(services)

    async def trigger_service(
        self,
        domain: str,
        service: str,
        **service_data,
    ) -> List[State]:
        """Tells homeassistant to trigger a service, returns stats changed while being called"""
        data = await self.async_request(
            path("services", domain, service),
            method="POST",
            json=service_data,
        )
        return [
            self.process_state_json(state_data)
            for state_data in cast(List[Dict[Any, Any]], data)
        ]

    # EntityState methods
    async def get_state(
        self,
        entity_id: str = None,
        group: str = None,
        slug: str = None,
    ) -> State:
        """Fetches the state of the entity specified"""
        if group is not None and slug is not None:
            entity_id = group + "." + slug
        elif entity_id is None:
            raise ValueError("Neither group and slug or entity_id provided.")
        data = await self.async_request(path("states", entity_id))
        return self.process_state_json(cast(Dict[Any, Any], data))

    async def set_state(
        self,
        entity_id: str = None,
        state: str = None,
        group: str = None,
        slug: str = None,
        **payload,
    ) -> State:
        """Sets the state of the entity given (does not have to be a real entity) and returns the updated state"""
        if group is None or slug is None:
            raise ValueError(
                "To use group or slug you need to pass both not just one."
                "Make sure you are using keyword arguments."
            )
        if group is not None and slug is not None:
            entity_id = group + "." + slug
        elif entity_id is None:
            raise ValueError("Neither group and slug or entity_id provided.")
        if state is None:
            raise ValueError('required parameter "state" is missing')
        payload.update(state=state)
        data = await self.async_request(
            path("states", entity_id), method="POST", json=payload
        )
        return self.process_state_json(cast(Dict[Any, Any], data))

    async def get_states(self) -> List[State]:
        """Gets the states of all entitites within homeassistant"""
        data = await self.async_request("states")
        return [
            self.process_state_json(state_data)
            for state_data in cast(List[Dict[Any, Any]], data)
        ]

    # Event methods
    async def get_events(self) -> JsonModel:
        """Gets the Events that happen within homeassistant"""
        data = await self.async_request("events")
        if not isinstance(data, list):
            events = [
                self.process_event_json(event_info)
                for event_info in cast(List[Dict[Any, Any]], data)
            ]
            return JsonModel({evt.event_type: evt for evt in events})
        raise TypeError()  # TODO: Add error description here

    async def fire_event(self, event_type: str, **event_data) -> str:
        """Fires a given event_type within homeassistant. Must be an existing event_type."""
        data = await self.async_request(
            path("events", event_type), method="POST", json=event_data
        )
        if not isinstance(data, dict):
            raise TypeError(
                f"Invalid return type from API. Expected {dict!r} got {type(data)!r}"
            )
        return data.get("message", "No message provided")
