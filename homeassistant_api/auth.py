from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from homeassistantapi.client import Client
 

class AccessToken:
    """Abstract class for dealing with authentication information for Home Assistant instances."""

    def token(self, client: "Client") -> str:
        """Method for getting an authentication token. Long Lived Tokens will not change, but OAuth2 can use this to automatically refresh their access token every so often."""
        raise NotImplementedError(f"Please use a subclass of {type(self)!r}")


class LongLived(AccessToken):
    """Stores and provides Long Lived Access Tokens (that do not change) for your py:meth:`Client`."""
 
    def __init__(self) -> None:
        self._token = token

    def token(self, client: "Client") -> str:
        return self._token


class OAuth2(AccessToken):
    def token(self, client: "Client") -> str:
        pass

