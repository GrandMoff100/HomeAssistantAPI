from datetime import datetime

from .models import Group, Entity, State, Domain
from .errors import APIConfigurationError, HTTPError
from .rawapi import RawWrapper


class RawClient(RawWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.check_api_running()
        self.check_api_config()

    def _process_entity_json(self, json: dict):
        pass

    def _process_service_json(self, json: dict):
        pass

    def _process_state_json(self, json: dict):
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
        pass
    
    def get_state(self):
        pass
    
    def set_state(self):
        pass
    
    def get_states(self):
        pass
    
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
