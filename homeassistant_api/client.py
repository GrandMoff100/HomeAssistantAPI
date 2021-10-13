"""Module for Client class"""

from datetime import datetime
from os.path import join as path
from typing import List, Union, Tuple, Coroutine

from .models import Group, Entity, State, Domain, JsonModel, Event
from .errors import APIConfigurationError, MalformedInputError
from .rawapi import RawWrapper


FMT = '%Y-%m-%dT%H:%M:%S%z'


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
        domain = Domain(json.get('domain'), self)
        for service_id, data in json.get('services').items():
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
        return self.request('error_log')

    def api_config(self) -> dict:
        """Returns the yaml configuration of homeassistant"""
        return self.request('config')

    def logbook_entries(
        self,
        filter_entity: Entity = None,
        timestamp: Union[str, datetime] = None,  # Defaults to 1 day before
        end_timestamp: Union[str, datetime] = None
    ) -> Union[List[dict], Coroutine]:
        params = {}
        if filter_entity is not None:
            params.update(entity=filter_entity.entity_id)
        if end_timestamp is not None:
            if isinstance(end_timestamp, datetime):
                end_timestamp = end_timestamp.strftime(FMT)
            params.update(end_time=end_timestamp)
        if timestamp is not None:
            if isinstance(timestamp, datetime):
                timestamp = timestamp.strftime(FMT)
            url = path('logbook', timestamp)
        else:
            url = 'logbook'
        return self.request(url, params=params)

    def get_history(
        self,
        entities: Tuple[Entity] = None,
        timestamp: datetime = None,  # Defaults to 1 day before
        end_timestamp: datetime = None,
        minimal_state_data=False,
        significant_changes_only=False
    ) -> Union[dict, list, str, Coroutine]:
        params = {}
        if entities is not None:
            params.update(filter_entity_id=','.join([ent.entity_id for ent in entities]))
        if end_timestamp:
            end_timestamp = end_timestamp.strftime(FMT)
            params.update(end_time=end_timestamp)
        if minimal_state_data:
            params.update(minimal_response=None)
        if significant_changes_only:
            params.update(significant_changes_only=None)
        if timestamp is not None:
            if isinstance(timestamp, datetime):
                timestamp = timestamp.strftime(FMT)
            url = path('history/period', timestamp)
        else:
            url = 'history/period'
        return self.request(url, params=self.construct_params(params))

    def get_rendered_template(self, template: str) -> str:
        return self.request('template', json=dict(template=template), return_text=True, method='POST')

    def get_discovery_info(self) -> dict:
        """Returns a dictionary of discovery info such as internal_url and version"""
        res = self.request('discovery_info')
        return res

    # API check methods
    def check_api_config(self) -> True:
        """Asks homeassistant to validate its configuration file"""
        res = self.request('config/core/check_config', method='POST')
        valid = {'valid': True, 'invalid': False}.get(res['result'], None)
        if not valid:
            raise APIConfigurationError(res['errors'])
        return valid

    def check_api_running(self) -> True:
        """Asks homeassistant if its running"""
        res = self.request('')
        if res.get('message', None) == 'API running.':
            return True
        else:
            raise ValueError('Server response did not return message attribute')

    def malformed_id(self, entity_id: str) -> bool:
        """Checks whether or not a given entity_id is formatted correctly"""
        checks = [
            ' ' in entity_id,
            '.' not in entity_id,
            '-' in entity_id,
            entity_id.lower() == entity_id
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
            group_id, entity_slug = state.entity_id.split('.')
            entities[group_id].add_entity(entity_slug, state)
        return JsonModel(entities)

    def get_entity(
        self,
        group_id: str = None,
        entity_slug: str = None,
        entity_id: str = None
    ) -> Entity:
        """Returns a Entity model for an entity_id"""
        if group_id is not None and entity_slug is not None:
            state = self.get_state(group=group_id, slug=entity_slug)
        elif entity_id is not None:
            state = self.get_state(entity_id=entity_id)
        else:
            raise ValueError(
                'Neither group and slug or entity_id provided. {help_msg}'.format(
                    help_msg='Use keyword arguments to pass entity_id. Or you can pass the entity_group and entity_slug instead'
                )
            )
        group_id, entity_slug = state.entity_id.split('.')
        group = Group(group_id, self)
        group.add_entity(entity_slug, state)
        return group.get_entity(entity_slug)

    # Services and domain methods
    def get_domains(self) -> JsonModel:
        """Fetches all Services from the api"""
        services = self.request('services')
        services = [self.process_services_json(data) for data in services]
        services = {service.domain_id: service for service in services}
        return JsonModel(services)

    def trigger_service(
        self,
        domain: str,
        service: str,
        **service_data
    ) -> List[State]:
        """Tells homeassistant to trigger a service, returns stats changed while being called"""
        data = self.request(
            path(
                'services',
                domain,
                service
            ),
            method='POST',
            json=service_data
        )
        return [
            self.process_state_json(state_data)
            for state_data in data
        ]

    # EntityState methods
    def get_state(self, entity_id: str = None, group: str = None, slug: str = None) -> State:
        """Fetches the state of the entity specified"""
        if group is not None and slug is not None:
            entity_id = group + '.' + slug
        elif entity_id is None:
            raise ValueError('Neither group and slug or entity_id provided.')
        if self.malformed_id(entity_id):
            raise MalformedInputError(f"The entity_id, {entity_id!r}, is malformed")
        data = self.request(path('states', entity_id))
        return self.process_state_json(data)

    def set_state(self, entity_id: str = None, state: str = None, group: str = None, slug: str = None, **payload) -> State:
        """Sets the state of the entity given (does not have to be a real entity) and returns the updated state"""
        if (group is None or slug is None) and entity_id is None:
            raise ValueError('To use group or slug you need to pass both not just one. '
                             'Make sure you are using keyword arguments.')
        if group is not None and slug is not None:
            entity_id = group + '.' + slug
        elif entity_id is None:
            raise ValueError('Neither group and slug or entity_id provided.')
        if self.malformed_id(entity_id):
            raise MalformedInputError(f"The entity_id, {entity_id!r}, is malformed")
        if state is None:
            raise ValueError('required parameter "state" is missing')
        payload.update(state=state)
        data = self.request(
            path('states', entity_id),
            method='POST',
            json=payload
        )
        return self.process_state_json(data)

    def get_states(self) -> List[State]:
        """Gets the states of all entitites within homeassistant"""
        data = self.request('states')
        return [self.process_state_json(state_data) for state_data in data]

    # Event methods
    def get_events(self) -> JsonModel:
        """Gets the Events that happen within homeassistant"""
        data = self.request('events')
        events = [self.process_event_json(event_info) for event_info in data]
        events = {evt.event_type: evt for evt in events}
        return JsonModel(events)

    def fire_event(self, event_type: str, **event_data) -> str:
        """Fires a given event_type within homeassistant. Must be an existing event_type."""
        data = self.request(
            path(
                'events',
                event_type
            ),
            method='POST',
            json=event_data
        )
        return data.get('message', 'No message provided')


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
