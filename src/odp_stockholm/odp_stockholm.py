"""Asynchronous Python client for ODP Stockholm."""

from __future__ import annotations

import asyncio
import socket
from copy import deepcopy
from dataclasses import dataclass
from importlib import metadata
from typing import Any, Self

from aiohttp import ClientError, ClientSession
from aiohttp.hdrs import METH_GET
from yarl import URL

from .exceptions import ODPStockholmConnectionError, ODPStockholmError
from .models import DisabledParking, ParkingCollection, ParkingSpot, ParkingType

VERSION = metadata.version("odp-stockholm")


@dataclass
class ParkingStockholm:
    """Main class for handling data fetching from Parking Platform of Stockholm."""

    api_key: str
    request_timeout: float = 15.0
    session: ClientSession | None = None

    _close_session: bool = False

    async def _request(
        self,
        uri: str,
        *,
        method: str = METH_GET,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Handle a request to the Open Data Platform API of Stockholm.

        Args:
        ----
            uri: Request URI, without '/', for example, 'status'
            method: HTTP method to use, for example, 'GET'
            params: Extra options to improve or limit the response.

        Returns:
        -------
            A Python dictionary (text) with the response from
            the Open Data Platform API of Stockholm.

        Raises:
        ------
            ODPStockholmConnectionError: An error occurred while
                communicating with the Open Data Platform API of Stockholm.
            ODPStockholmError: Received an unexpected response from
                the Open Data Platform API of Stockholm.

        """
        url = URL.build(
            scheme="https",
            host="openparking.stockholm.se",
            path="/LTF-Tolken/v1/",
        ).join(
            URL(uri),
        )

        headers = {
            "Accept": "application/json",
            "User-Agent": f"PythonODPStockholm/{VERSION}",
        }

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        try:
            async with asyncio.timeout(self.request_timeout):
                response = await self.session.request(
                    method,
                    url,
                    params=params,
                    headers=headers,
                    ssl=True,
                )
                response.raise_for_status()
        except TimeoutError as exception:
            msg = "Timeout occurred while connecting to the Open Data Platform API."
            raise ODPStockholmConnectionError(msg) from exception
        except (ClientError, socket.gaierror) as exception:
            msg = "Error occurred while communicating with the Open Data Platform API."
            raise ODPStockholmConnectionError(msg) from exception

        content_type = response.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            msg = "Unexpected content type response from the Open Data Platform API"
            raise ODPStockholmError(msg)

        try:
            return await response.json()
        except ValueError:
            msg = "Invalid JSON response from the Open Data Platform API"
            raise ODPStockholmError(msg) from None

    async def parking_collection(
        self,
        *,
        parking_type: ParkingType = ParkingType.DISABLED,
        max_records: int = 10000,
    ) -> ParkingCollection:
        """Retrieve all permit-holder regulations with count and identity checks.

        The endpoint supports a single full response. A safety ceiling is never
        permission to truncate. Response time is not a dataset revision; validity
        dates and source identifiers carry no promise of long-term stability.
        """
        if parking_type != ParkingType.DISABLED:
            msg = "Unsupported Stockholm parking selection"
            raise ValueError(msg)
        if type(max_records) is not int or max_records < 1:
            msg = "max_records must be a positive integer"
            raise ValueError(msg)
        data = await self._request(
            "prorelsehindrad/all",
            params={
                "maxFeatures": max_records + 1,
                "outputFormat": "json",
                "apiKey": self.api_key,
            },
        )
        try:
            return self._collection(data, max_records)
        except (ValueError, TypeError, KeyError, AttributeError):
            msg = "Incomplete or malformed Stockholm parking collection"
            raise ODPStockholmError(msg) from None

    @staticmethod
    def _collection(data: Any, max_records: int) -> ParkingCollection:
        """Validate metadata and preserve original features without lossy parsing."""
        if (
            not isinstance(data, dict)
            or data.get("type") != "FeatureCollection"
            or data.get("crs", {}).get("properties", {}).get("name")
            != "urn:ogc:def:crs:EPSG::4326"
            or not isinstance(data.get("features"), list)
        ):
            raise ValueError
        features = data["features"]
        count = data["numberMatched"]
        if (
            type(count) is not int
            or not 0 <= count <= max_records
            or type(data["numberReturned"]) is not int
            or data["numberReturned"] != count
            or type(data["totalFeatures"]) is not int
            or data["totalFeatures"] != count
            or len(features) != count
        ):
            raise ValueError
        records = []
        seen = set()
        for feature in features:
            if not isinstance(feature, dict) or feature.get("type") != "Feature":
                raise ValueError
            properties = feature["properties"]
            geometry = feature["geometry"]
            fid = properties["FID"]
            record_id = feature["id"]
            if (
                type(fid) is not int
                or fid < 1
                or record_id != f"LTFR_P_RORELSEHINDRADE.{fid}"
                or record_id in seen
                or not isinstance(geometry, dict)
                or geometry.get("type") not in {"LineString", "MultiLineString"}
                or not isinstance(geometry.get("coordinates"), list)
            ):
                raise ValueError
            street = properties.get("STREET_NAME")
            if street is not None and not isinstance(street, str):
                raise ValueError
            seen.add(record_id)
            records.append(
                ParkingSpot(record_id, deepcopy(geometry), street, deepcopy(feature))
            )
        return ParkingCollection(records, count, 1, None)

    async def disabled_parkings(
        self,
        limit: int = 10,
    ) -> list[DisabledParking]:
        """Get a list of disabled parkings.

        Args:
        ----
            limit: Limit the number of results.

        Returns:
        -------
            A list of DisabledParking objects.

        """
        locations = await self._request(
            "prorelsehindrad/all",
            params={
                "maxFeatures": limit,
                "outputFormat": "json",
                "apiKey": self.api_key,
            },
        )
        return [
            DisabledParking.from_json(location) for location in locations["features"]
        ]

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> Self:
        """Async enter.

        Returns
        -------
            The Open Data Platform Stockholm object.

        """
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Async exit.

        Args:
        ----
            _exc_info: Exec type.

        """
        await self.close()
