import sys


class Error(BaseException):
    pass


class HTTPError(Error):
    pass


class MalformedDataError(Error):
    pass


class APIConfigurationError(Error):
    pass