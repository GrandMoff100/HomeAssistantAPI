"""Module for custom error classes"""


class Error(BaseException):
    """Base class for custom errors"""


class RequestError(Error):
    """Error raised when an issue occurs when requesting to Homeassistant."""

    def __init__(self, body: str):
        super().__init__(f"Bad Request: {body}")

class MalformedDataError(Error):
    """Error raised when data from api is not formatted as JSON"""


class MalformedInputError(Error):
    """Error raised when user passes malformed data in parameters"""


class APIConfigurationError(Error):
    """Error raised when api says it has an invalid configuration file"""


class ParameterMissingError(Error):
    """Error raised when an expected attribute is missing from api response data."""


class UnexpectedStatusCodeError(Error):
    """Error raised when Homeassistant returns a response with status code that was unexpected."""
    
    def __init__(self, code: int):
        super().__init__(f"Homeassistant return response with an unrecognized status code {code!r}")


class UnauthorizedError(Error):
    """Error raised when an invalid token in used to authenticate with homeassistant."""

    def __init__(self):
        super().__init__("Invalid authentication token")


class EndpointNotFoundError(Error):
    """Error raised when a request is made to a non existing endpoint."""

    def __init__(self, path: str):
        super().__init__(f"Cannot make request to the endpoint {path!r}")


class MethodNotAllowedError(Error):
    """Error raised when a request is made to an endpoint with a non-allowed method."""

    def __init__(self, method: str):
        super().__init__(f"Request made with invalid method {method!r}")
