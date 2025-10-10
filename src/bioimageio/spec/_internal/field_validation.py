from __future__ import annotations

from datetime import date, datetime
from typing import (
    Any,
    Hashable,
    Mapping,
    Sequence,
    Union,
)

import httpx

from ._settings import settings
from .constants import KNOWN_GITHUB_USERS, KNOWN_INVALID_GITHUB_USERS
from .field_warning import issue_warning
from .type_guards import is_mapping, is_sequence, is_tuple
from .validation_context import get_validation_context


def is_valid_yaml_leaf_value(value: Any) -> bool:
    return value is None or isinstance(value, (bool, date, datetime, int, float, str))


def is_valid_yaml_key(value: Union[Any, Sequence[Any]]) -> bool:
    return (
        is_valid_yaml_leaf_value(value)
        or is_tuple(value)
        and all(is_valid_yaml_leaf_value(v) for v in value)
    )


def is_valid_yaml_mapping(value: Union[Any, Mapping[Any, Any]]) -> bool:
    return is_mapping(value) and all(
        is_valid_yaml_key(k) and is_valid_yaml_value(v) for k, v in value.items()
    )


def is_valid_yaml_sequence(value: Union[Any, Sequence[Any]]) -> bool:
    return is_sequence(value) and all(is_valid_yaml_value(v) for v in value)


def is_valid_yaml_value(value: Any) -> bool:
    return any(
        is_valid(value)
        for is_valid in (
            is_valid_yaml_key,
            is_valid_yaml_mapping,
            is_valid_yaml_sequence,
        )
    )


def validate_unique_entries(seq: Sequence[Hashable]):
    if len(seq) != len(set(seq)):
        raise ValueError("Entries are not unique.")
    return seq


def validate_github_user(
    username: str, hotfix_known_errorenous_names: bool = True
) -> str:
    if hotfix_known_errorenous_names:
        if username == "Constantin Pape":
            return "constantinpape"

    if (
        username.lower() in KNOWN_GITHUB_USERS
        or not get_validation_context().perform_io_checks
    ):
        return username

    if username.lower() in KNOWN_INVALID_GITHUB_USERS:
        raise ValueError(f"Known invalid GitHub user '{username}'")

    try:
        r = httpx.get(
            f"https://api.github.com/users/{username}",
            auth=settings.github_auth,
            timeout=settings.http_timeout,
        )
    except httpx.TimeoutException:
        issue_warning(
            "Could not verify GitHub user '{value}' due to connection timeout",
            value=username,
        )
    else:
        if r.status_code == 403 and r.reason_phrase == "rate limit exceeded":
            issue_warning(
                "Could not verify GitHub user '{value}' due to GitHub API rate limit",
                value=username,
            )
        elif r.status_code != 200:
            KNOWN_INVALID_GITHUB_USERS.add(username.lower())
            raise ValueError(f"Could not find GitHub user '{username}'")

        KNOWN_GITHUB_USERS.add(username.lower())

    return username
