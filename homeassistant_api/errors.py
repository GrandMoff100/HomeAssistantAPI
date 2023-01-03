"""Module for custom error classes"""

from typing import Union


class HomeassistantAPIError(BaseException):
    """Base class for custom errors"""


class RequestError(HomeassistantAPIError):
    """Error raised when an issue occurs when requesting to Homeassistant."""


class RequestTimeoutError(RequestError):
    """Error raised when a request times out."""


class ResponseError(HomeassistantAPIError):
    """Error raised when an issue occurs in a response from Homeassistant."""


class BadTemplateError(HomeassistantAPIError):
    """Error raised when User sends bad template to homeassistant."""


class MalformedDataError(HomeassistantAPIError):
    """Error raised when data from api is not formatted as JSON"""


class MalformedInputError(HomeassistantAPIError):
    """Error raised when user passes malformed data in parameters"""


class APIConfigurationError(HomeassistantAPIError):
    """Error raised when api says it has an invalid configuration file"""


class ParameterMissingError(HomeassistantAPIError):
    """Error raised when an expected attribute is missing from api response data."""


class InternalServerError(HomeassistantAPIError):
    """Error raised when Home Assistant says that it got itself in trouble."""

    def __init__(self, status_code: int, content: Union[str, bytes]) -> None:
        super().__init__(
            f"Home Assistant returned a response with an error status code {status_code!r}.\n"
            f"{content!r}\n"
            "If this happened, "
            "please report it at https://github.com/GrandMoff100/HomeAssistantAPI/issues "
            "with the request status code and the request content. Thanks!"
        )


class UnauthorizedError(HomeassistantAPIError):
    """Error raised when an invalid token in used to authenticate with homeassistant."""

    def __init__(self):
        super().__init__("Invalid authentication token")


class EndpointNotFoundError(HomeassistantAPIError):
    """Error raised when a request is made to a non existing endpoint."""

    def __init__(self, path: str):
        super().__init__(f"Cannot make request to the endpoint {path!r}")


class MethodNotAllowedError(HomeassistantAPIError):
    """Error raised when a request is made to an endpoint with a non-allowed method."""

    def __init__(self, method: str) -> None:
        super().__init__(f"Request made with invalid method {method!r}")


class ProcessorNotFoundError(HomeassistantAPIError):
    """
    Error raised when a response is encountered that homeassistant_api is not told how to handle.
    """


class UnexpectedStatusCodeError(ResponseError):
    """Error raised when a response has an unexpected status code."""

    def __init__(self, status_code: int) -> None:
        super().__init__(f"Response has unexpected status code: {status_code!r}")
