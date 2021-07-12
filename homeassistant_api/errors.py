class Error(BaseException):
    pass


class MalformedDataError(Error):
    pass


class HTTPError(Error):
    pass


class APIConfigurationError(Error):
    pass


class ParameterMissingError(Error):
    pass
