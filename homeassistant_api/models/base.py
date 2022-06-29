"""Module for Global Base Model Configuration inheritance."""

from datetime import datetime

from pydantic import BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel):
    """Base model that all Library Models inherit from."""

    class Config:  # pylint: disable=too-few-public-methods
        """Pydantic config class for all library models."""

        arbitrary_types_allowed = True
        smart_union = True
        validate_assignment = True
        exclude_none = True

        json_encoders = {
            datetime: lambda timestamp: timestamp.isoformat(),
        }
