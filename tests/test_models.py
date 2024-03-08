"""Test the models for ODP Stockholm."""

from __future__ import annotations

from aiohttp import ClientSession
from aresponses import ResponsesMockServer

from odp_stockholm import DisabledParking, ParkingStockholm

from . import load_fixtures


async def test_all_disabled_parkings(aresponses: ResponsesMockServer) -> None:
    """Test all disabled parkings function."""
    aresponses.add(
        "openparking.stockholm.se",
        "/LTF-Tolken/v1/prorelsehindrad/all",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("disabled_parking.json"),
        ),
    )
    async with ClientSession() as session:
        client = ParkingStockholm(api_key="test", session=session)
        parking: list[DisabledParking] = await client.disabled_parkings()
        assert parking is not None
