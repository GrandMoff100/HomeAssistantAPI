"""Module for Global Base Model Configuration inheritance."""

from pydantic import BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel):
    """Base model that all Library Models inherit from."""

    class Config:
        """Pydantic config class for all library models."""

        arbitrary_types_allowed = True
        smart_union = True
        validate_assignment = True
