"""Exercise complete retrieval and failure contracts without live credentials."""

import json
from copy import deepcopy
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from aresponses import ResponsesMockServer

from odp_stockholm import (
    DisabledParking,
    ODPStockholmError,
    ParkingStockholm,
    ParkingType,
)

from . import load_fixtures


def complete_response() -> dict[str, Any]:
    """Make the historical sample a complete, small test selection."""
    data = json.loads(load_fixtures("disabled_parking.json"))
    data.update(totalFeatures=5, numberMatched=5, numberReturned=5)
    return data


async def test_complete_collection_preserves_source_claims() -> None:
    """Keep line types, identity and attributes without inventing a revision."""
    data = complete_response()
    data["features"][0]["properties"]["VF_PLATSER"] = 2
    data["features"][1]["properties"].pop("STREET_NAME")
    data["features"][1]["geometry"] = {
        "type": "MultiLineString",
        "coordinates": [[[18.09, 59.29], [18.10, 59.30]]],
    }
    async with ParkingStockholm(api_key="fake") as client:
        with patch.object(client, "_request", AsyncMock(return_value=data)) as request:
            result = await client.parking_collection(
                parking_type=ParkingType.DISABLED, max_records=5
            )
    request.assert_awaited_once_with(
        "prorelsehindrad/all",
        params={"maxFeatures": 6, "outputFormat": "json", "apiKey": "fake"},
    )
    assert result.complete
    assert result.total_count == 5
    assert result.pages_fetched == 1
    assert result.source_version is None
    assert result.records[0].spot_id == "LTFR_P_RORELSEHINDRADE.6205721"
    assert result.records[0].geometry == data["features"][0]["geometry"]
    assert result.records[0].source_attributes == data["features"][0]
    assert result.records[1].street is None
    data["features"][0]["properties"]["VF_PLATSER"] = 99
    assert result.records[0].source_attributes["properties"]["VF_PLATSER"] == 2


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("numberMatched", 6),
        ("numberMatched", "5"),
        ("numberMatched", True),
        ("numberReturned", 4),
        ("numberReturned", 5.0),
        ("totalFeatures", 4),
        ("totalFeatures", "unknown"),
        ("features", {}),
        ("type", "wrong"),
        ("crs", None),
        ("crs", {"properties": {"name": "EPSG:3006"}}),
    ],
)
async def test_inconsistent_metadata_is_rejected(field: str, value: object) -> None:
    """Reject truncated, wrong-CRS and uncounted responses."""
    data = complete_response()
    data[field] = value
    async with ParkingStockholm(api_key="fake") as client:
        with (
            patch.object(client, "_request", AsyncMock(return_value=data)),
            pytest.raises(ODPStockholmError),
        ):
            await client.parking_collection()


@pytest.mark.parametrize(
    "mutation",
    [
        "duplicate",
        "missing-fid",
        "bad-fid",
        "bad-id",
        "point",
        "street",
        "properties",
        "feature-type",
    ],
)
async def test_invalid_features_are_rejected(mutation: str) -> None:
    """Never deliver malformed or duplicate features."""
    data = complete_response()
    feature = data["features"][0]
    if mutation == "duplicate":
        data["features"][1] = deepcopy(feature)
    elif mutation == "missing-fid":
        del feature["properties"]["FID"]
    elif mutation == "bad-fid":
        feature["properties"]["FID"] = True
    elif mutation == "bad-id":
        feature["id"] = "another-id"
    elif mutation == "point":
        feature["geometry"]["type"] = "Point"
    elif mutation == "street":
        feature["properties"]["STREET_NAME"] = 3
    elif mutation == "feature-type":
        feature["type"] = "wrong"
    else:
        feature["properties"] = None
    async with ParkingStockholm(api_key="fake") as client:
        with (
            patch.object(client, "_request", AsyncMock(return_value=data)),
            pytest.raises(ODPStockholmError),
        ):
            await client.parking_collection()


async def test_ceiling_does_not_truncate_and_empty_can_be_complete() -> None:
    """The package proves empty selections; the consumer decides to deliver them."""
    data = complete_response()
    async with ParkingStockholm(api_key="fake") as client:
        with patch.object(client, "_request", AsyncMock(return_value=data)):
            with pytest.raises(ODPStockholmError):
                await client.parking_collection(max_records=4)
            data.update(features=[], totalFeatures=0, numberMatched=0, numberReturned=0)
            result = await client.parking_collection()
    assert result.records == []
    assert result.total_count == 0
    assert result.complete


@pytest.mark.parametrize("ceiling", [0, -1, True, 1.5])
async def test_invalid_ceiling_never_requests_source(ceiling: int) -> None:
    """Bad caller arguments fail before requesting the source."""
    async with ParkingStockholm(api_key="fake") as client:
        with (
            patch.object(client, "_request", AsyncMock()) as request,
            pytest.raises(ValueError, match="positive integer"),
        ):
            await client.parking_collection(max_records=ceiling)
    request.assert_not_awaited()


async def test_non_json_authentication_response_does_not_expose_body(
    aresponses: ResponsesMockServer,
) -> None:
    """Unexpected responses and malformed JSON never enter a collection."""
    for content_type, body in [
        ("text/html", "secret"),
        ("application/json", ""),
        ("application/json", "{"),
    ]:
        aresponses.add(
            "openparking.stockholm.se",
            "/LTF-Tolken/v1/prorelsehindrad/all",
            "GET",
            aresponses.Response(
                status=200, headers={"Content-Type": content_type}, text=body
            ),
        )
        async with ParkingStockholm(api_key="fake") as client:
            with pytest.raises(ODPStockholmError) as error:
                await client.parking_collection()
        assert "secret" not in str(error.value)
        assert "fake" not in str(error.value)


async def test_inspection_capacity_uses_optional_bay_count() -> None:
    """Extent identity must never be interpreted as thousands of parking bays."""
    feature = complete_response()["features"][0]
    feature["properties"]["EXTENT_NO"] = 4475
    assert DisabledParking.from_json(feature).number is None
    feature["properties"]["VF_PLATSER"] = 2
    assert DisabledParking.from_json(feature).number == 2


@pytest.mark.parametrize("parking_type", ["pbuss"])
async def test_unknown_selection_never_requests_source(
    parking_type: ParkingType,
) -> None:
    """A different regulatory selection cannot be mislabeled as disabled parking."""
    async with ParkingStockholm(api_key="fake") as client:
        with (
            patch.object(client, "_request", AsyncMock()) as request,
            pytest.raises(ValueError, match="Unsupported Stockholm parking selection"),
        ):
            await client.parking_collection(parking_type=parking_type)
    request.assert_not_awaited()
