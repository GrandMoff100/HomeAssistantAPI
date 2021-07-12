from datetime import datetime
from os.path import join as path

from .models import Group, Entity, State, Domain
from .errors import APIConfigurationError, HTTPError
from .rawapi import RawWrapper


class RawClient(RawWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.check_api_running()
        self.check_api_config()

    def process_entity_json(self, json: dict):
        pass

    def process_services_json(self, json: dict):
        domain = Domain(json.get('domain'), self)
        for service_id, data in json.get('services').items():
            domain.add_service(service_id, **data)
        return domain


    def process_state_json(self, json: dict):
        pass

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
        pass
    
    def rendered_template(self, template: str):
        pass
    
    def check_api_config(self):
        res = self.request('config/core/check_config', method='POST')
        valid = {'valid': True, 'invalid': False}.get(res['result'], None)
        if not valid:
            raise APIConfigurationError(res['errors'])
        return valid

    def check_api_running(self):
        res = self.request('')
        if res.get('message', None) == 'API running.':
            return True
        else:
            raise HTTPError(res.get('message', 'No response'))

    def get_discovery_info(self):
        res = self.request('discovery_info')
        return res

    def malformed_id(self, entity_id):
        checks = [
            ' ' in entity_id,
            '.' not in entity_id
        ]
        return True in checks

    def get_entity(self, group_id: str = None, entity_slug: str = None, entity_id: str = None):
        if group_id is not None and entity_slug is not None:
            pass
        elif entity_id is not None:
            pass
        else:
            raise ValueError('Neither group and slug or entity_id provided.')
    
    def get_entities(self):
        pass
    
    def get_service(self, domain: str, service: str):
        pass
    
    def trigger_service(self, domain: str, service: str):
        pass

    def get_services(self):
        services = self.request('services')
        services = [self.process_services_json(data) for data in services]
        return services
    
    def get_state(self, entity_id: str = None, group: str = None, slug: str = None):
        if group is not None and slug is not None:
            entity_id = group + '.' + slug
        elif entity_id is None:
            raise ValueError('Neither group and slug or entity_id provided.')
        data = self.request(path('states', entity_id))
        return State(**data)

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
        return State(**data)
    
    def get_states(self):
        data = self.request('states')
        return [State(**state_data) for state_data in data]

    def get_history(
        self, 
        entities: tuple = None,
        entity: Entity = None,
        start_date: datetime = None,  # Defaults to 1 day before
        end_date: datetime = None,
        minimal_state_data=False,
        big_changes_only=False
    ):
        pass


class Client(RawClient):
    pass
