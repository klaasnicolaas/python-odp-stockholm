# pylint: disable=W0621
"""Asynchronous Python client providing Open Data information of Stockholm."""

import asyncio

from odp_stockholm import ParkingStockholm


async def main() -> None:
    """Show example on using the Parking Stockholm API client."""
    async with ParkingStockholm(
        api_key="YOUR_API_KEY",
    ) as client:
        locations = await client.disabled_parkings(
            limit=50,
        )

        count: int = len(locations)
        for item in locations:
            print(item)

        # Count unique id's in disabled_parkings
        unique_values: list[str] = [str(item.location_id) for item in locations]
        num_values = len(set(unique_values))

        print("__________________________")
        print(f"Total locations found: {count}")
        print(f"Unique ID values: {num_values}")


if __name__ == "__main__":
    asyncio.run(main())
