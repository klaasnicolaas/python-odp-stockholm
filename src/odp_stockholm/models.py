"""Asynchronous Python client for ODP Stockholm."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import pytz


@dataclass
class DisabledParking:
    """Object representing an DisabledParking model response from the API."""

    location_id: int
    location_type: str

    number: int
    street: str
    address: str
    district: str
    parking_rate: str
    parking_rules: str

    valid_from: datetime
    valid_to: datetime | None
    coordinates: list[float]

    @classmethod
    def from_json(cls: type[DisabledParking], data: dict[str, Any]) -> DisabledParking:
        """Return DisabledParking object from a dictionary.

        Args:
        ----
            data: The JSON data from the API.

        Returns:
        -------
            An DisabledParking object.

        """
        attr = data["properties"]
        return cls(
            location_id=attr["FID"],
            location_type=attr["VF_PLATS_TYP"],
            number=attr["EXTENT_NO"],
            street=attr["STREET_NAME"],
            address=attr["ADDRESS"],
            district=attr["CITY_DISTRICT"],
            parking_rate=attr["PARKING_RATE"],
            parking_rules=attr["RDT_URL"],
            valid_from=strptime(
                attr.get("VALID_FROM"),
                "%Y-%m-%dT%H:%M:%SZ",
            ),
            valid_to=strptime(
                attr.get("VALID_TO"),
                "%Y-%m-%dT%H:%M:%SZ",
            ),
            coordinates=data["geometry"]["coordinates"],
        )


def strptime(date_string: str, date_format: str, default: None = None) -> Any:
    """Strptime function with default value.

    Args:
    ----
        date_string: The date string.
        date_format: The format of the date string.
        default: The default value.

    Returns:
    -------
        The datetime object.

    """
    try:
        return datetime.strptime(date_string, date_format).astimezone(
            pytz.timezone("UTC"),
        )
    except (ValueError, TypeError):
        return default
