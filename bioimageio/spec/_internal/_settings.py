from typing import Optional, Union

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Annotated


class Settings(BaseSettings, extra="ignore"):
    """environment variables for bioimageio.spec"""

    model_config = SettingsConfigDict(
        env_prefix="BIOIMAGEIO_", env_file=".env", env_file_encoding="utf-8"
    )

    github_username: Optional[str] = None
    """GitHub username for API requests"""

    github_token: Optional[str] = None
    """GitHub token for API requests"""

    log_warnings: bool = True
    """log validation warnings to console"""

    perform_io_checks: bool = True
    """wether or not to perform validation that requires file io,
    e.g. downloading a remote files.

    Existence of local absolute file paths is still being checked."""

    CI: Annotated[Union[bool, str], Field(alias="CI")] = False
    """wether or not the execution happens in a continuous integration (CI) environment"""

    user_agent: Optional[str] = None
    """user agent for http requests"""

    @property
    def github_auth(self):
        if self.github_username is None or self.github_token is None:
            return None
        else:
            return (self.github_username, self.github_token)


settings = Settings()
