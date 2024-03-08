"""Asynchronous Python client for ODP Stockholm."""

from __future__ import annotations

import asyncio
import socket
from dataclasses import dataclass
from importlib import metadata
from typing import Any, Self, cast

from aiohttp import ClientError, ClientSession
from aiohttp.hdrs import METH_GET
from yarl import URL

from .exceptions import ODPStockholmConnectionError, ODPStockholmError
from .models import DisabledParking


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
        version = metadata.version(__package__)
        url = URL.build(
            scheme="https",
            host="openparking.stockholm.se",
            path="/LTF-Tolken/v1/",
        ).join(
            URL(uri),
        )

        headers = {
            "Accept": "application/json",
            "User-Agent": f"PythonODPStockholm/{version}",
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
            text = await response.text()
            msg = "Unexpected content type response from the Open Data Platform API"
            raise ODPStockholmError(
                msg,
                {"Content-Type": content_type, "response": text},
            )

        return cast(dict[str, Any], await response.json())

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
