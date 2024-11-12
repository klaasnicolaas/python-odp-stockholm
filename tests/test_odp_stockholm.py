"""Basic tests for ODP Stockholm."""

# pylint: disable=protected-access
import asyncio
from unittest.mock import patch

import pytest
from aiohttp import ClientError, ClientResponse, ClientSession
from aresponses import Response, ResponsesMockServer

from odp_stockholm import ParkingStockholm
from odp_stockholm.exceptions import ODPStockholmConnectionError, ODPStockholmError

from . import load_fixtures


async def test_json_request(
    aresponses: ResponsesMockServer, odp_stockholm_client: ParkingStockholm
) -> None:
    """Test JSON response is handled correctly."""
    aresponses.add(
        "openparking.stockholm.se",
        "/LTF-Tolken/v1/test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("disabled_parking.json"),
        ),
    )
    await odp_stockholm_client._request("test")
    await odp_stockholm_client.close()


async def test_internal_session(aresponses: ResponsesMockServer) -> None:
    """Test internal session is handled correctly."""
    aresponses.add(
        "openparking.stockholm.se",
        "/LTF-Tolken/v1/test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("disabled_parking.json"),
        ),
    )
    async with ParkingStockholm(api_key="test") as client:
        await client._request("test")


async def test_timeout(aresponses: ResponsesMockServer) -> None:
    """Test request timeout from the Open Data Platform API of Stockholm."""

    # Faking a timeout by sleeping
    async def response_handler(_: ClientResponse) -> Response:
        await asyncio.sleep(0.2)
        return aresponses.Response(
            body="Goodmorning!",
            text=load_fixtures("disabled_parking.json"),
        )

    aresponses.add(
        "openparking.stockholm.se",
        "/LTF-Tolken/v1/test",
        "GET",
        response_handler,
    )

    async with ClientSession() as session:
        client = ParkingStockholm(
            api_key="test",
            session=session,
            request_timeout=0.1,
        )
        with pytest.raises(ODPStockholmConnectionError):
            assert await client._request("test")


async def test_content_type(
    aresponses: ResponsesMockServer, odp_stockholm_client: ParkingStockholm
) -> None:
    """Test request content type error from Open Data Platform API of Stockholm."""
    aresponses.add(
        "openparking.stockholm.se",
        "/LTF-Tolken/v1/test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "blabla/blabla"},
        ),
    )
    with pytest.raises(ODPStockholmError):
        assert await odp_stockholm_client._request("test")


async def test_client_error() -> None:
    """Test request client error from the Open Data Platform API of Stockholm."""
    async with ClientSession() as session:
        client = ParkingStockholm(api_key="test", session=session)
        with (
            patch.object(
                session,
                "request",
                side_effect=ClientError,
            ),
            pytest.raises(ODPStockholmConnectionError),
        ):
            assert await client._request("test")
