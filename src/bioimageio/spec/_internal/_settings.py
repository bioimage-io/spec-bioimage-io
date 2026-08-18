from __future__ import annotations

import os
from functools import cached_property
from pathlib import Path
from typing import Any

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

    def __setattr__(self, name: str, value: Any):
        super().__setattr__(name, value)
        # if cache_path is being changed, we need to reset the disk_cache so that it gets re-created with the new path when accessed next time
        if (
            name == "cache_path"
            and "disk_cache" in self.__dict__
            and self.disk_cache.dir_path != value
        ):
            del self.disk_cache

    @field_validator("cache_path", mode="after")
    @classmethod
    def _expand_user(cls, value: Path):
        return Path(os.path.expanduser(str(value)))

    CI: Annotated[bool | str, Field(alias="CI")] = False
    """Wether or not the execution happens in a continuous integration (CI) environment."""

    collection_http_pattern: str = (
        "https://hypha.aicell.io/bioimage-io/artifacts/{bioimageio_id}/files/rdf.yaml"
    )
    """A pattern to map bioimageio IDs to bioimageio.yaml URLs.
    Notes:
    - '{bioimageio_id}' is replaced with user query,
      e.g. "affable-shark" when calling `load_description("affable-shark")`.
    - This method takes precedence over resolving via `id_map`.
    - If this endpoints fails, we fall back to `id_map`.
    """

    github_username: str | None = None
    """GitHub username for API requests"""

    github_token: str | None = None
    """GitHub token for API requests"""

    http_timeout: float = 10.0
    """Timeout in seconds for http requests."""

    huggingface_http_pattern: str = (
        "https://huggingface.co/{repo_id}/resolve/{branch}/package/bioimageio.yaml"
    )
    """A pattern to map huggingface repo IDs to bioimageio.yaml URLs.
    Notes:
    - Used for loading source strings of the form "huggingface/{user_or_org}/{resource_id}[/{version}]"
    - example use: `load_description("huggingface/fynnbe/ambitious-sloth/1.3")`
    - A given version {version} is mapped to a branch name "v{version}", e.g. "v1.3".
    - If no version is provided the "main" branch is used.
    - This method takes precedence over resolving via `id_map`.
    - If this endpoints fails, we fall back to `id_map`.
    """

    hypha_upload: str = (
        "https://hypha.aicell.io/public/services/artifact-manager/create"
    )
    """URL to the upload endpoint for bioimageio resources."""

    hypha_upload_token: str | None = None
    """Hypha API token to use for uploads.

    By setting this token you agree to our terms of service at https://bioimage.io/#/toc.

    How to obtain a token:
        1. Login to https://bioimage.io
        2. Generate a new token at https://bioimage.io/#/api?tab=hypha-rpc
    """

    id_map: str = (
        "https://uk1s3.embassy.ebi.ac.uk/public-datasets/bioimage.io/id_map.json"
    )
    """URL to bioimageio id_map.json to resolve resource IDs."""

    id_map_draft: str = (
        "https://uk1s3.embassy.ebi.ac.uk/public-datasets/bioimage.io/id_map_draft.json"
    )
    """URL to bioimageio id_map_draft.json to resolve draft IDs ending with '/draft'."""

    log_warnings: bool = True
    """Log validation warnings to console."""

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

    user_agent: str | None = None
    """user agent for http requests"""

    @cached_property
    def disk_cache(self):
        cache = DiskCache[RootHttpUrl].create(
            url_type=RootHttpUrl,
            cache_dir=self.cache_path,
            url_hasher=UrlDigest.from_str,
        )
        return cache

    @property
    def github_auth(self):
        if self.github_username is None or self.github_token is None:
            return None
        else:
            return (self.github_username, self.github_token)


settings = Settings()
"""parsed environment variables for bioimageio.spec"""
