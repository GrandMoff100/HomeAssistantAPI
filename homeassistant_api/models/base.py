"""File for base data model types"""

from typing import Any


class JsonModel(dict):
    """Makes dict values available as object attributes"""
    def __init__(self, json: dict = None, **kwargs) -> None:
        """Updates self with passed json data and kwargs"""
        if json:
            self.update(json)
        if kwargs:
            self.update(kwargs)

    def __getattr__(self, name: str) -> Any:
        """Searches for a key name in self if not found returns from parent attributes"""
        if '__' not in str(name):
            if name in self:
                if isinstance(self[name], dict):
                    return JsonModel(self[name])
                return self[name]
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value: Any) -> None:
        """Sets values as dictionary entries if not dunder methods or attributes"""
        if '__' not in str(name):
            if isinstance(value, dict):
                self[name] = JsonModel(value)
            self[name] = value
        super().__setattr__(name, value)
