import re
from distutils.version import StrictVersion
from pathlib import Path
from typing import Optional

import pytest
from ruamel.yaml import YAML

from bioimageio.spec import cummulative
from bioimageio import spec
from bioimageio.spec.utils import get_args

yaml = YAML(typ="safe")


@pytest.fixture
def rf_config_path_v0_1():
    return Path(__file__).parent / "../example_specs/models/sklearn/RandomForestClassifier_v0_1.model.yaml"


@pytest.fixture
def rf_config_path_v0_3_1():
    return Path(__file__).parent / "../example_specs/models/sklearn/RandomForestClassifier_v0_3_1.model.yaml"


@pytest.fixture
def rf_config_path_v0_3_2():
    return Path(__file__).parent / "../example_specs/models/sklearn/RandomForestClassifier_v0_3_2.model.yaml"


@pytest.fixture
def rf_config_path_v0_3(rf_config_path_v0_3_2):
    return rf_config_path_v0_3_2


@pytest.fixture
def rf_config_path(rf_config_path_v0_3_2):
    return rf_config_path_v0_3_2


def get_unet2d_nuclei_broad_path(version: str):
    assert isinstance(version, str), version
    assert "_" not in version, version
    assert "." in version, version
    if version == spec.__version__:
        version = ""  # latest version without specifier
    else:
        version = "_" + version.replace(".", "_")

    return Path(__file__).parent / f"../example_specs/models/unet2d_nuclei_broad/rdf{version}.yaml"


def pytest_generate_tests(metafunc):
    # generate
    #   - unet2d_nuclei_broad_[before_]v{major}_{minor}[_{patch}]_path
    #   - unet2d_nuclei_broad_[before_]latest_path
    #   - unet2d_nuclei_broad_any_path
    all_format_versions = [fv for mfv in get_args(cummulative.ModelFormatVersion) for fv in get_args(mfv)]
    for fixture_name in metafunc.fixturenames:
        m = re.fullmatch(
            (
                r"unet2d_nuclei_broad_("
                r"((?P<before>before_)?((v(?P<major>\d+)_(?P<minor>\d+)(_(?P<patch>\d+))?)|(?P<latest>latest)))"
                r"|"
                r"(?P<any>any)"
                r")_path"
            ),
            fixture_name,
        )
        if not m:
            continue

        if m["any"]:
            vs = all_format_versions
        else:
            if m["latest"]:
                v = spec.__version__
            else:
                major = m["major"]
                minor = m["minor"]
                patch = m["patch"]
                if patch is None:  # default to latest patch
                    patch = getattr(spec, f"v{major}_{minor}").__version__.split(".")[-1]

                v = ".".join([major, minor, patch])

            if m["before"]:
                vs = [vv for vv in all_format_versions if StrictVersion(vv) < StrictVersion(v)]
            else:
                vs = [v]

        metafunc.parametrize(fixture_name, map(get_unet2d_nuclei_broad_path, vs))


@pytest.fixture
def FruNet_model_url():
    return "https://raw.githubusercontent.com/deepimagej/models/master/fru-net_sev_segmentation/model.yaml"
