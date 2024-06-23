import functools
from google.api_core.exceptions import (
    DeadlineExceeded,
    InternalServerError,
    ResourceExhausted,
)
import logging
import time
from typing import (
    Any,
    Callable,
    ParamSpec,
    TypeVar,
)


P = ParamSpec("P")
R = TypeVar("R")
F = Callable[P, R]


_MAX_INTERNAL_SERVER_ERRORS = 5


def retry_on_server_error(func: F) -> F:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        wait_time = 1
        try_count = 1
        while True:
            try:
                return func(*args, **kwargs)
            except (DeadlineExceeded, InternalServerError) as e:
                if try_count >= _MAX_INTERNAL_SERVER_ERRORS:
                    raise

                logging.exception(e)
                try_count += 1
            except ResourceExhausted as e:
                logging.exception(e)
                time.sleep(wait_time)
                if wait_time < 1024:
                    wait_time *= 2

    return wrapper
