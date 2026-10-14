"""Asynchronous Python client for ODP Stockholm."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class ParkingType(StrEnum):
    """Selections supported by the complete parking collection API."""

    DISABLED = "prorelsehindrad"


@dataclass
class ParkingSpot:
    """A source feature retaining its identity, geometry and every source field."""

    id: str
    geometry: dict[str, Any]
    street: str | None
    source_attributes: dict[str, Any]


@dataclass
class ParkingCollection:
    """A complete source selection, never a capped inspection result."""

    records: list[ParkingSpot]
    total_count: int
    pages_fetched: int
    source_version: str | None
    complete: bool = True


@dataclass
class DisabledParking:
    """Object representing an DisabledParking model response from the API."""

    location_id: int
    location_type: str | None

    number: int | None
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
            location_type=attr.get("VF_PLATS_TYP"),
            number=attr.get("VF_PLATSER"),
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
