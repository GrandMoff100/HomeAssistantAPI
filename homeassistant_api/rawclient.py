import os
import json
import requests
from .states import Entity
from .servicedomains import Domain
from .errors import MalformedDataError, APIConfigurationError, HTTPError
from .models import DictAttrs


class RawWrapper:
    def __init__(self, api_url, token):
        self.api_url = api_url
        if not self.api_url.endswith('/'):
            self.api_url += '/'
        self._token = token

    def endpoint(self, path):
        url = os.path.join(self.api_url, path)
        return url
    
    @property
    def _headers(self):
        return {
            "Authorization": f"Bearer {self._token}",
            "content-type": "application/json",
        }

    def request(self, path, method='GET', headers={}, **kwargs):
        req = getattr(requests, method.lower())
        
        url = self.endpoint(path)
        headers.update(self._headers)
        
        resp = req(
            url,
            headers=headers,
            **kwargs
        )

        try:
            res = resp.json()
        except json.decoder.JSONDecodeError:
            try:
                code, msg = resp.text.split(': ')
            except ValueError:
                return resp.text
            else:
                err_msg = ': '.join([code, url, msg, f'with method "{method.upper()}"'])
                raise HTTPError(err_msg)
        else:
            return res


class RawClient(RawWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.check_api_running()
        self.check_api_config()

    def _process_entity_json(self, json):
        group = json['entity_id'].split('.')[0]
        entity = self._entity_types.get(group, Entity)
        return entity(json)

    def _process_domain_json(self, json):
        dom = Domain(json, self)
        return dom

    @property
    def _entity_types(self):
        types = Entity.__subclasses__()
        return {t.group:t for t in types}

    def api_error_log(self):
        res = self.request('error_log')
        return res.splitlines()
    
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
    
    def get_api_config(self):
        res = self.request('config')
        return res

    def get_entities(self):
        res = self.request('states')
        return [self._process_entity_json(json) for json in res]
    
    def get_entity(self, entity_id):
        if self.malformed_id(entity_id):
            raise MalformedDataError('"{}" is not a valid entity_id, check your spelling and try again.'.format(entity_id))
        res = self.request(f'states/{entity_id}')
        return self._process_entity_json(res)

    def get_discovery_info(self):
        res = self.request('discovery_info')
        return res
    
    def get_services(self):
        res = self.request('services')
        domains = [self._process_domain_json(domain) for domain in res]
        domains = {dom.domain_id:dom for dom in domains}
        return DictAttrs(domains)
    
    def malformed_id(self, entity_id):
        checks = [
            ' ' in entity_id,
            '.' not in entity_id
        ]
        return True in checks

    def get_events(self):
        res = self.request('events')
        return res
    
    def get_service_domain(self, group: str):
        return self.get_services().get(group, None)
    
    def get_entity_group(self, group: str):
        return list(filter(
            lambda x: x.group == group,
            self.get_entities()
        ))