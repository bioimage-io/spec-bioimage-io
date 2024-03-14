import logging
import re

import pytest

from bioimageio.spec._internal.warning_levels import ALERT, INFO, WARNING


@pytest.mark.parametrize("unit", ["lx·s", "kg/m^2·s^-2"])
def test_si_unit(unit: str):
    from bioimageio.spec._internal.constants import SI_UNIT_REGEX

    assert re.fullmatch(SI_UNIT_REGEX, unit)


@pytest.mark.parametrize("unit", ["lxs", " kg", "kg/m^-2"])
def test_invalid_si_uni(unit: str):
    from bioimageio.spec._internal.constants import SI_UNIT_REGEX

    assert not re.fullmatch(SI_UNIT_REGEX, unit)


def test_warning_levels():
    """test that our warning levels nicely match python's logging module's levels"""
    assert ALERT < logging.ERROR
    assert ALERT > logging.WARNING
    assert WARNING == logging.WARNING
    assert INFO == logging.INFO


def test_known_gh_users_are_lowercase():
    from bioimageio.spec._internal.constants import (
        KNOWN_GH_USERS,
        KNOWN_INVALID_GH_USERS,
    )

    assert KNOWN_GH_USERS == {user.lower() for user in KNOWN_GH_USERS}
    assert KNOWN_INVALID_GH_USERS == {user.lower() for user in KNOWN_INVALID_GH_USERS}
