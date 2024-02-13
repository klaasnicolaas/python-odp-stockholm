<!-- Banner -->
![alt Banner of the ODP Stockholm package](https://raw.githubusercontent.com/klaasnicolaas/python-odp-stockholm/main/assets/header_odp_stockholm-min.png)

<!-- PROJECT SHIELDS -->
[![GitHub Release][releases-shield]][releases]
[![Python Versions][python-versions-shield]][pypi]
![Project Stage][project-stage-shield]
![Project Maintenance][maintenance-shield]
[![License][license-shield]](LICENSE)

[![GitHub Activity][commits-shield]][commits-url]
[![PyPi Downloads][downloads-shield]][downloads-url]
[![GitHub Last Commit][last-commit-shield]][commits-url]
[![Open in Dev Containers][devcontainer-shield]][devcontainer]

[![Build Status][build-shield]][build-url]
[![Typing Status][typing-shield]][typing-url]
[![Maintainability][maintainability-shield]][maintainability-url]
[![Code Coverage][codecov-shield]][codecov-url]


Asynchronous Python client for the open datasets of Stockholm (Sweden).

## About

A python package with which you can retrieve data from the Open Data Platform of Stockholm via [their API][api]. This package was initially created to only retrieve parking data from the API, but the code base is made in such a way that it is easy to extend for other datasets from the same platform.

## Installation

```bash
pip install odp-stockholm
```

## Datasets

You can read the following datasets with this package:

- [Disabled parkings / rörelsehindrade förare med särskilt tillstånd][parking_api]

To use the data you need an API key, which you can request via [this link][request_api_key].

<details>
    <summary>Click here to get more details</summary>

### Disabled parkings (2045 locations)

You can use the following parameters in your request:

- **limit** (default: 10) - How many results you want to retrieve.

| Variable | Type | Description |
| :------- | :--- | :---------- |
| `location_id` | string | The id of the location |
| `location_type` | string | The type of the location |
| `number` | integer | How many parking spots there are on this location |
| `street` | string | The street name of the location |
| `address` | string | The address of the location |
| `district` | string | The district name where the location is |
| `parking_rate` | string | The parking rate of the location |
| `parking_rules` | string | URL to the parking regulations of Stockholm |
| `valid_from` | datetime | The date from when the parking is valid |
| `valid_to` | datetime (or None) | The date until when the parking is valid |
| `coordinates` | list[float] | The coordinates of the location |
</details>

### Example

```python
import asyncio

from odp_stockholm import ParkingStockholm


async def main() -> None:
    """Show example on using this package."""
    async with ParkingStockholm(api_key="YOUR_API_KEY") as client:
        locations = await client.disabled_parkings(
            limit=10,
        )
        print(locations)


if __name__ == "__main__":
    asyncio.run(main())
```

## Contributing

This is an active open-source project. We are always open to people who want to
use the code or contribute to it.

We've set up a separate document for our
[contribution guidelines](CONTRIBUTING.md).

Thank you for being involved! :heart_eyes:

## Setting up development environment

The simplest way to begin is by utilizing the [Dev Container][devcontainer]
feature of Visual Studio Code or by opening a CodeSpace directly on GitHub.
By clicking the button below you immediately start a Dev Container in Visual Studio Code.

[![Open in Dev Containers][devcontainer-shield]][devcontainer]

This Python project relies on [Poetry][poetry] as its dependency manager,
providing comprehensive management and control over project dependencies.

You need at least:

- Python 3.11+
- [Poetry][poetry-install]

Install all packages, including all development requirements:

```bash
poetry install
```

Poetry creates by default an virtual environment where it installs all
necessary pip packages, to enter or exit the venv run the following commands:

```bash
poetry shell
exit
```

Setup the pre-commit check, you must run this inside the virtual environment:

```bash
pre-commit install
```

*Now you're all set to get started!*

As this repository uses the [pre-commit][pre-commit] framework, all changes
are linted and tested with each commit. You can run all checks and tests
manually, using the following command:

```bash
poetry run pre-commit run --all-files
```

To run just the Python tests:

```bash
poetry run pytest
```

## License

MIT License

Copyright (c) 2023-2024 Klaas Schoute

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<!-- LINKS FROM PLATFORM -->
[api]: https://dataportalen.stockholm.se
[parking_api]: https://openstreetgs.stockholm.se/Home/Parking
[request_api_key]: https://openstreetgs.stockholm.se/Home/Key

<!-- MARKDOWN LINKS & IMAGES -->
[build-shield]: https://github.com/klaasnicolaas/python-odp-stockholm/actions/workflows/tests.yaml/badge.svg
[build-url]: https://github.com/klaasnicolaas/python-odp-stockholm/actions/workflows/tests.yaml
[codecov-shield]: https://codecov.io/gh/klaasnicolaas/python-odp-stockholm/branch/main/graph/badge.svg?token=ZMROLN54BK
[codecov-url]: https://codecov.io/gh/klaasnicolaas/python-odp-stockholm
[commits-shield]: https://img.shields.io/github/commit-activity/y/klaasnicolaas/python-odp-stockholm.svg
[commits-url]: https://github.com/klaasnicolaas/python-odp-stockholm/commits/main
[devcontainer-shield]: https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode
[devcontainer]: https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/klaasnicolaas/python-odp-stockholm
[downloads-shield]: https://img.shields.io/pypi/dm/odp-stockholm
[downloads-url]: https://pypistats.org/packages/odp-stockholm
[last-commit-shield]: https://img.shields.io/github/last-commit/klaasnicolaas/python-odp-stockholm.svg
[license-shield]: https://img.shields.io/github/license/klaasnicolaas/python-odp-stockholm.svg
[maintainability-shield]: https://api.codeclimate.com/v1/badges/181c219e4ac665fda7cd/maintainability
[maintainability-url]: https://codeclimate.com/github/klaasnicolaas/python-odp-stockholm/maintainability
[maintenance-shield]: https://img.shields.io/maintenance/yes/2024.svg
[project-stage-shield]: https://img.shields.io/badge/project%20stage-production%20ready-brightgreen.svg
[pypi]: https://pypi.org/project/odp-stockholm/
[python-versions-shield]: https://img.shields.io/pypi/pyversions/odp-stockholm
[releases-shield]: https://img.shields.io/github/release/klaasnicolaas/python-odp-stockholm.svg
[releases]: https://github.com/klaasnicolaas/python-odp-stockholm/releases
[typing-shield]: https://github.com/klaasnicolaas/python-odp-stockholm/actions/workflows/typing.yaml/badge.svg
[typing-url]: https://github.com/klaasnicolaas/python-odp-stockholm/actions/workflows/typing.yaml

[poetry-install]: https://python-poetry.org/docs/#installation
[poetry]: https://python-poetry.org
[pre-commit]: https://pre-commit.com
