"""Module for custom error classes"""


class Error(BaseException):
    """Base class for custom errors"""


class MalformedDataError(Error):
    """Error raised when data from api is not formatted as JSON"""


class MalformedInputError(Error):
    """Error raised when user passes malformed data in parameters"""


class ResponseError(Error):
    """Error raised when an api response is formatted unexpectedly."""


class APIConfigurationError(Error):
    """Error raised when api says it has an invalid configuration file"""


class ParameterMissingError(Error):
    """Error raised when an expected attribute is missing from api response data"""
