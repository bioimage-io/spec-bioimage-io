from pathlib import Path
from typing import Optional, Union

import pooch
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Annotated


class Settings(BaseSettings, extra="ignore"):
    """environment variables for bioimageio.spec"""

    model_config = SettingsConfigDict(
        env_prefix="BIOIMAGEIO_", env_file=".env", env_file_encoding="utf-8"
    )

    cache_path: Path = pooch.os_cache("bioimageio")
    """bioimageio cache location"""

    collection: str = (
        "https://uk1s3.embassy.ebi.ac.uk/public-datasets/bioimage.io/collection.json"
    )
    """url to bioimageio collection.json to resolve collection specific resource IDs.
    """

    collection_staged: str = (
        "https://uk1s3.embassy.ebi.ac.uk/public-datasets/bioimage.io/collection_staged.json"
    )
    """url to bioimageio collection_staged.json to resolve collection specific, staged
    resource IDs."""

    resolve_staged: bool = True
    """Flag to resolve staged resource versions following the pattern
    <resource id>/staged/<stage number>.
    Note that anyone may stage a new resource version and that such a staged version
    may not have been reviewed.
    Set this flag to False to avoid this potential security risk."""

    perform_io_checks: bool = True
    """wether or not to perform validation that requires file io,
    e.g. downloading a remote files.

    Existence of any local absolute file paths is still being checked."""

    log_warnings: bool = True
    """log validation warnings to console"""

    github_username: Optional[str] = None
    """GitHub username for API requests"""

    github_token: Optional[str] = None
    """GitHub token for API requests"""

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
