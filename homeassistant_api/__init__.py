from .client import Client, RawClient
from .models import Group, Entity, Domain, Service, State, Event
from .processing import Processing
from .errors import (
    HomeassistantAPIError,
    RequestError,
    MalformedDataError,
    MalformedInputError,
    APIConfigurationError,
    ParameterMissingError,
    UnexpectedStatusCodeError,
    UnauthorizedError,
    EndpointNotFoundError,
    MethodNotAllowedError
)

__version__ = '2.4.0.post2'
__name__ = 'Homeassistant API'
