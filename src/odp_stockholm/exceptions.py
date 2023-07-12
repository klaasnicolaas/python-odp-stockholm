"""Asynchronous Python client providing Open Data information of Stockholm."""


class ODPStockholmError(Exception):
    """Generic Open Data Platform exception."""


class ODPStockholmConnectionError(ODPStockholmError):
    """Open Data Platform connection exception."""
