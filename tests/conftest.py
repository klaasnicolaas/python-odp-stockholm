"""Fixture for the ODP Stockholm tests."""

from collections.abc import AsyncGenerator

import pytest
from aiohttp import ClientSession

from odp_stockholm import ParkingStockholm


@pytest.fixture(name="odp_stockholm_client")
async def client() -> AsyncGenerator[ParkingStockholm, None]:
    """Return an ODP Stockholm client."""
    async with (
        ClientSession() as session,
        ParkingStockholm(api_key="FakeKey", session=session) as odp_stockholm_client,
    ):
        yield odp_stockholm_client
