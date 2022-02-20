"""Imports all library stuff for convenience."""
from .client import Client
from .errors import (
    APIConfigurationError,
    EndpointNotFoundError,
    HomeassistantAPIError,
    MalformedDataError,
    MalformedInputError,
    MethodNotAllowedError,
    ParameterMissingError,
    RequestError,
    UnauthorizedError,
    UnexpectedStatusCodeError,
)
from .models import Domain, Entity, Event, Group, History, Service, State
from .processing import Processing
