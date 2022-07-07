"""Module for Calendar and CalendarEvent data models."""
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple

from .base import BaseModel

if TYPE_CHECKING:
    from homeassistant_api import Client


class CalendarEvent(BaseModel):
    """Model representing a calendar event within Home Assistant."""

    summary: str
    start: datetime
    end: datetime
    all_day: bool
    description: Optional[str] = None
    location: Optional[str] = None

    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> "CalendarEvent":
        """Process the calendar event json."""
        if "date" in json.get("start", {}) or "date" in json.get("end", {}):
            json["all_day"] = True
        if start_date_string := json.get("start", {}).get("dateTime") or json.get(
            "start", {}
        ).get("date"):
            json["start"] = datetime.fromisoformat(start_date_string)
        if end_date_string := json.get("end", {}).get("dateTime") or json.get(
            "end", {}
        ).get("date"):
            json["end"] = datetime.fromisoformat(end_date_string)
        return cls.parse_obj(json)


class Calendar(BaseModel):
    """Model representing calendar entities within Home Assistant."""

    entity_id: str
    name: str
    _client: "Client"

    def __init__(self, *args, _client: Optional["Client"] = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        assert _client is not None
        self._client = _client

    @classmethod
    def from_json(
        cls,
        json: Dict[str, Any],
        _client: Optional["Client"] = None,
    ) -> "Calendar":
        """Process the calendar json."""
        assert _client is not None
        return cls(**json, _client=_client)

    def get_calendar_events(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> Tuple[CalendarEvent, ...]:
        """Get all events for the calendar."""
        return self._client.get_calendar_events(
            self.entity_id,
            start_time,
            end_time,
        )

    async def async_get_calendar_events(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> Tuple[CalendarEvent, ...]:
        """Get all events for the calendar."""
        return await self._client.async_get_calendar_events(
            self.entity_id,
            start_time,
            end_time,
        )
