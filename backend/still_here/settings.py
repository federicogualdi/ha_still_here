"""PS settings."""

import sys

from collections.abc import Callable
from functools import wraps

from loguru import logger
from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    """Application settings.

    Args:
        BaseSettings (BaseSettings): pydantic BaseSettings class
    """

    model_config = SettingsConfigDict(case_sensitive=True)

    debug: bool = Field(False, validation_alias="DEBUG")
    wait_for_debugger_connected: bool = Field(False, validation_alias="WAIT_FOR_DEBUGGER")
    log_level: str = Field("INFO", validation_alias="LOG_LEVEL")
    enable_auth: bool = Field(True, validation_alias="ENABLE_AUTH")

    def __init__(self, *args, **kwargs) -> None:
        """Init settings."""
        super().__init__(*args, **kwargs)
        self._set_log_level()

    def _set_log_level(self):
        try:
            logger.remove(0)
        except ValueError:
            logger.debug("No default logger found, already removed")
        try:
            # create only one logger sink, if not already created
            if not logger._core.handlers:  # noqa: SLF001
                logger.add(sys.stderr, level=self.log_level)
                logger.debug(f"Logger initialized in this component with log level: {self.log_level}")
            else:
                logger.debug("Logger already initialized in another component, use that one")
        except ValueError:
            logger.exception("Error setting log level")


settings = Settings()


# TODO: setup auth provider
def init_auth_provider() -> None:
    """Initialize authorization provider.

    Returns:
        AbstractAuthentication | None: AuthenticationProvider or None based on auth settings
    """
    # initialize authentication provider
    auth = None
    if settings.enable_auth:
        ...
    return auth


def authentication_provider(  # noqa ANN201
    *args,
    **kwargs,
):
    """Authentication decorator builder."""

    def decorator(  # noqa ANN202
        func,  # noqa ANN201
    ):
        @wraps(func)
        def wrapper(*args, **kwargs):  # noqa ANN202
            return func(*args, **kwargs)

        return wrapper

    return decorator


def get_auth(read_metadata: Callable, context_arg_index: int):  # noqa: ANN201
    """Get the auth decorator."""
    return authentication_provider(
        auth=init_auth_provider(),  # type: ignore
        read_metadata=read_metadata,
        context_arg_index=context_arg_index,
    )


def get_logger():  # noqa: ANN201
    """Get logger."""
    return logger
