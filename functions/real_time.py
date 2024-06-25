from datetime import datetime
import logging


async def current_datetime() -> str:
    """Returns the current date and time.

    Returns:
        The current date and time.
    """
    logging.info("Getting the current date and time.")
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
