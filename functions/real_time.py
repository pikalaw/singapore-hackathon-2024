"""A collection of functions related to real-time information."""

import datetime
import zoneinfo
import logging


async def current_datetime(timezone: str = "America/New_York") -> str:
    """Returns the current date and time.

    Args:
        timezone: The timezone to use.

    Returns:
        The current date and time.
    """
    logging.info("Getting the current date and time in %s.", timezone)
    tz = zoneinfo.ZoneInfo(timezone)

    return datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
