from ..models import JsonModel, DictAttrs
from .service import Service


class BaseDomain(JsonModel):
    def __init__(self, json):
        self.domain = None
        self.services = None
        
        super().__init__(json)

    def __str__(self):
        return ''.join([x.capitalize() for x in self.domain.split('_')])


class Domain:
    def __init__(self, json, client):
        self.__base = BaseDomain(json)
        self.name = str(self.__base)
        self.services = DictAttrs({
            service_id:Service(self.domain_id, service_id, json, client)
            for service_id, json in self.__base.services.items()    
        })
    
    def __str__(self):
        return self.name + 'Domain'
    
    def __repr__(self):
        return f'<{self.name} services>'
    
    @property
    def domain_id(self):
        return self.__base.domain
