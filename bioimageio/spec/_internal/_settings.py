from pathlib import Path
from typing import Optional, Union

import pooch  # pyright: ignore [reportMissingTypeStubs]
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

    id_map: str = (
        "https://uk1s3.embassy.ebi.ac.uk/public-datasets/bioimage.io/id_map.json"
    )
    """url to bioimageio id_map.json to resolve resource IDs.
    """

    id_map_draft: str = (
        "https://uk1s3.embassy.ebi.ac.uk/public-datasets/bioimage.io/id_map_draft.json"
    )
    """url to bioimageio id_map_draft.json to resolve draft IDs ending with '/draft'."""

    resolve_draft: bool = True
    """Flag to resolve draft resource versions following the pattern
    <resource id>/draft.
    Note that anyone may stage a new draft and that such a draft version
    may not have been reviewed yet.
    Set this flag to False to avoid this potential security risk
    and disallow loading draft versions."""

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
"""parsed environment variables for bioimageio.spec"""
