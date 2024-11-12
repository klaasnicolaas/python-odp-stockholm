"""Test the models for ODP Stockholm."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aresponses import ResponsesMockServer
from syrupy.assertion import SnapshotAssertion

from . import load_fixtures

if TYPE_CHECKING:
    from odp_stockholm import DisabledParking, ParkingStockholm


async def test_all_disabled_parkings(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    odp_stockholm_client: ParkingStockholm,
) -> None:
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
    parking: list[DisabledParking] = await odp_stockholm_client.disabled_parkings()
    assert parking == snapshot
