"""Asynchronous Python client for ODP Stockholm."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any


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
            valid_from=datetime.strptime(
                attr.get("VALID_FROM"),
                "%Y-%m-%dT%H:%M:%SZ",
            ).replace(tzinfo=UTC),
            valid_to=datetime.strptime(
                attr.get("VALID_TO"),
                "%Y-%m-%dT%H:%M:%SZ",
            ).replace(tzinfo=UTC)
            if attr.get("VALID_TO")
            else None,
            coordinates=data["geometry"]["coordinates"],
        )
