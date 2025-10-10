import os
from functools import cached_property
from pathlib import Path
from typing import Optional, Union

import platformdirs
from genericache import DiskCache
from genericache.digest import UrlDigest
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Annotated

from .root_url import RootHttpUrl


class Settings(
    BaseSettings, extra="ignore", allow_inf_nan=False, validate_assignment=True
):
    """environment variables for bioimageio.spec"""

    model_config = SettingsConfigDict(
        env_prefix="BIOIMAGEIO_", env_file=".env", env_file_encoding="utf-8"
    )

    allow_pickle: bool = False
    """Sets the `allow_pickle` argument for `numpy.load()`"""

    cache_path: Path = Path(platformdirs.user_cache_dir("bioimageio"))
    """bioimageio cache location"""

    @field_validator("cache_path", mode="after")
    @classmethod
    def _expand_user(cls, value: Path):
        return Path(os.path.expanduser(str(value)))

    collection_http_pattern: str = (
        "https://hypha.aicell.io/bioimage-io/artifacts/{bioimageio_id}/files/rdf.yaml"
    )
    """A pattern to map bioimageio IDs to bioimageio.yaml URLs.
    Notes:
    - '{bioimageio_id}' is replaced with user query,
      e.g. "affable-shark" when calling `load_description("affable-shark")`.
    - This method takes precedence over resolving via **id_map**.
    - If this endpoints fails, we fall back to **id_map**.
    """

    hypha_upload: str = (
        "https://hypha.aicell.io/public/services/artifact-manager/create"
    )
    """URL to the upload endpoint for bioimageio resources."""

    hypha_upload_token: Optional[str] = None
    """Hypha API token to use for uploads.

    By setting this token you agree to our terms of service at https://bioimage.io/#/toc.

    How to obtain a token:
        1. Login to https://bioimage.io
        2. Generate a new token at https://bioimage.io/#/api?tab=hypha-rpc
    """

    http_timeout: float = 10.0
    """Timeout in seconds for http requests."""

    id_map: str = (
        "https://uk1s3.embassy.ebi.ac.uk/public-datasets/bioimage.io/id_map.json"
    )
    """URL to bioimageio id_map.json to resolve resource IDs."""

    id_map_draft: str = (
        "https://uk1s3.embassy.ebi.ac.uk/public-datasets/bioimage.io/id_map_draft.json"
    )
    """URL to bioimageio id_map_draft.json to resolve draft IDs ending with '/draft'."""

    perform_io_checks: bool = True
    """Wether or not to perform validation that requires file io,
    e.g. downloading a remote files.

    Existence of any local absolute file paths is still being checked."""

    resolve_draft: bool = True
    """Flag to resolve draft resource versions following the pattern
    <resource id>/draft.

    Note that anyone may stage a new draft and that such a draft version
    may not have been reviewed yet.
    Set this flag to False to avoid this potential security risk
    and disallow loading draft versions."""

    log_warnings: bool = True
    """Log validation warnings to console."""

    github_username: Optional[str] = None
    """GitHub username for API requests"""

    github_token: Optional[str] = None
    """GitHub token for API requests"""

    CI: Annotated[Union[bool, str], Field(alias="CI")] = False
    """Wether or not the execution happens in a continuous integration (CI) environment."""

    user_agent: Optional[str] = None
    """user agent for http requests"""

    @property
    def github_auth(self):
        if self.github_username is None or self.github_token is None:
            return None
        else:
            return (self.github_username, self.github_token)

    @cached_property
    def disk_cache(self):
        cache = DiskCache[RootHttpUrl].create(
            url_type=RootHttpUrl,
            cache_dir=self.cache_path,
            url_hasher=UrlDigest.from_str,
        )
        return cache


settings = Settings()
"""parsed environment variables for bioimageio.spec"""
