from datetime import datetime
from os.path import join as path

from .models import Group, Entity, State, Domain, JsonModel
from .errors import APIConfigurationError, HTTPError
from .rawapi import RawWrapper


class RawClient(RawWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.check_api_running()
        self.check_api_config()

    # Response processing methods
    def process_entity_json(self, json: dict):
        pass

    def process_services_json(self, json: dict):
        domain = Domain(json.get('domain'), self)
        for service_id, data in json.get('services').items():
            domain.add_service(service_id, **data)
        return domain

    def process_state_json(self, json: dict):
        return State(**json)

    # API information methods
    def api_error_log(self):
        return self.request('error_log')

    def api_config(self):
        res = self.request('config')
        return res

    def logbook_entries(
        self,
        entity: Entity = None,
        start_date: datetime = None,  # Defaults to 1 day before
        end_date: datetime = None
    ):
        raise NotImplementedError('Not implemented in this pre-release as of 2.0a1')

    def get_history(
        self,
        entities: tuple = None,
        entity: Entity = None,
        start_date: datetime = None,  # Defaults to 1 day before
        end_date: datetime = None,
        minimal_state_data=False,
        big_changes_only=False
    ):
        raise NotImplementedError('Not implemented in this pre-release as of 2.0a1')

    def get_rendered_template(self, template: str):
        raise NotImplementedError('Not implemented in this pre-release as of 2.0a1')

    def get_discovery_info(self):
        res = self.request('discovery_info')
        return res

    # API check methods
    def check_api_config(self):
        res = self.request('config/core/check_config', method='POST')
        valid = {'valid': True, 'invalid': False}.get(res['result'], None)
        if not valid:
            raise APIConfigurationError(res['errors'])
        return valid

    def check_api_running(self):
        res = self.request('', return_text_if_fail=True)
        if isinstance(res, dict):
            if res.get('message', None) == 'API running.':
                return True
            else:
                print(res)
                # TODO: Replace with raise error
        else:
            raise HTTPError(res)

    def malformed_id(self, entity_id):
        checks = [
            ' ' in entity_id,
            '.' not in entity_id
        ]
        return True in checks

    # Entity methods
    def get_entities(self):
        class GroupDict(dict):
            def __missing__(cls, group_id: str):
                cls[group_id] = Group(group_id, self)
                return cls[group_id]
        entities = GroupDict()

        for state in self.get_states():
            group_id, entity_slug = state.entity_id.split('.')
            entities[group_id].add_entity(entity_slug, state)
        return JsonModel(entities)

    def get_entity(self, group_id: str = None, entity_slug: str = None, entity_id: str = None):
        if group_id is not None and entity_slug is not None:
            state = self.get_state(group=group_id, slug=entity_slug)
        elif entity_id is not None:
            state = self.get_state(entity_id=entity_id)
        else:
            raise ValueError('Neither group and slug or entity_id provided. {help_msg}'.format(
                help_msg='Use keyword arguments to pass entity_id. Or you can pass the entity_group and entity_slug instead'
            ))
        group_id, entity_slug = state.entity_id.split('.')
        group = Group(group_id, self)
        group.add_entity(entity_slug, state)
        return group.get_entity(entity_slug)

    # Services and domain methods
    def get_domains(self):
        services = self.request('services')
        services = [self.process_services_json(data) for data in services]
        services = {service.domain_id: service for service in services}
        return JsonModel(services)

    def trigger_service(self, domain: str, service: str, **service_data):
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
    def get_state(self, entity_id: str = None, group: str = None, slug: str = None):
        if group is not None and slug is not None:
            entity_id = group + '.' + slug
        elif entity_id is None:
            raise ValueError('Neither group and slug or entity_id provided.')
        data = self.request(path('states', entity_id))
        return self.process_state_json(data)

    def set_state(self, entity_id: str = None, state: str = None, group: str = None, slug: str = None, **payload):
        if group is None or slug is None:
            raise ValueError('To use group or slug you need to pass both not just one.'
                             'Make sure you are using keyword arguments.')
        if group is not None and slug is not None:
            entity_id = group + '.' + slug
        elif entity_id is None:
            raise ValueError('Neither group and slug or entity_id provided.')
        if state is None:
            raise ValueError('required parameter "state" is missing')
        payload.update(state=state)
        data = self.request(
            path('states', entity_id),
            method='POST',
            json=payload
        )
        return self.process_state_json(data)

    def get_states(self):
        data = self.request('states')
        return [self.process_state_json(state_data) for state_data in data]

    # Event methods
    def get_events(self):
        raise NotImplementedError('Not implemented in this pre-release as of 2.0a1')

    def fire_event(self):
        raise NotImplementedError('Not implemented in this pre-release as of 2.0a1')


class Client(RawClient):
    pass
