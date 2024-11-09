from __future__ import annotations

from datetime import date, datetime
from typing import (
    Any,
    Hashable,
    Mapping,
    Sequence,
    Union,
)

import requests

from ._settings import settings
from .constants import KNOWN_GH_USERS, KNOWN_INVALID_GH_USERS
from .field_warning import issue_warning
from .type_guards import is_mapping, is_sequence, is_tuple
from .validation_context import validation_context_var


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


def validate_gh_user(username: str, hotfix_known_errorenous_names: bool = True) -> str:
    if hotfix_known_errorenous_names:
        if username == "Constantin Pape":
            return "constantinpape"

    if (
        username.lower() in KNOWN_GH_USERS
        or not validation_context_var.get().perform_io_checks
    ):
        return username

    if username.lower() in KNOWN_INVALID_GH_USERS:
        raise ValueError(f"Known invalid GitHub user '{username}'")

    try:
        r = requests.get(
            f"https://api.github.com/users/{username}",
            auth=settings.github_auth,
            timeout=3,
        )
    except requests.exceptions.Timeout:
        issue_warning(
            "Could not verify GitHub user '{value}' due to connection timeout",
            value=username,
        )
    else:
        if r.status_code == 403 and r.reason == "rate limit exceeded":
            issue_warning(
                "Could not verify GitHub user '{value}' due to GitHub API rate limit",
                value=username,
            )
        elif r.status_code != 200:
            KNOWN_INVALID_GH_USERS.add(username.lower())
            raise ValueError(f"Could not find GitHub user '{username}'")

        KNOWN_GH_USERS.add(username.lower())

    return username
