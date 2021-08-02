import re
from distutils.version import StrictVersion
from pathlib import Path

import pytest

from bioimageio import spec
from bioimageio.spec import export_resource_package
from bioimageio.spec.shared.common import get_args_flat

try:
    from typing import get_args
except ImportError:
    from typing_extensions import get_args  # type: ignore


def get_unet2d_nuclei_broad_path(version: str):
    assert isinstance(version, str), version
    assert "_" not in version, version
    assert "." in version, version
    if version == spec.model.format_version:
        version = ""  # latest version without specifier
    else:
        version = "_v" + version.replace(".", "_")

    return Path(__file__).parent / f"../example_specs/models/unet2d_nuclei_broad/rdf{version}.yaml"


def get_package_from_rdf_path(rdf_path: Path):
    return export_resource_package(rdf_path)


def pytest_generate_tests(metafunc):
    # generate
    #   - unet2d_nuclei_broad_[before_]v{major}_{minor}[_{patch}][_package]_path
    #   - unet2d_nuclei_broad_[before_]latest[_package]_path
    #   - unet2d_nuclei_broad_any[_minor][_package]_path
    all_format_versions = get_args_flat(spec.model.FormatVersion)
    for fixture_name in metafunc.fixturenames:
        m = re.fullmatch(
            (
                r"unet2d_nuclei_broad_("
                r"((?P<before>before_)?((v(?P<major>\d+)_(?P<minor>\d+)(_(?P<patch>\d+))?)|(?P<latest>latest)))"
                r"|"
                r"(?P<any>any)(?P<any_minor>_minor)?"
                r")(?P<package>_package)?_path"
            ),
            fixture_name,
        )
        if not m:
            continue

        if m["any"]:
            vs = all_format_versions
            if m["any_minor"]:  # skip all patched versions
                vs_patched = {}
                for v in vs:
                    v_patched = tuple(v.split("."))
                    if v_patched > vs_patched.get(v_patched[:2], tuple()):
                        vs_patched[v_patched[:2]] = v_patched

                vs = [".".join(v) for v in vs_patched.values()]
        else:
            if m["latest"]:
                v = spec.model.format_version
            else:
                major = m["major"]
                minor = m["minor"]
                patch = m["patch"]
                if patch is None:  # default to latest patch
                    patched_version = get_args(getattr(spec.model, f"v{major}_{minor}").FormatVersion)[-1]
                    patch = patched_version.split(".")[-1]

                v = ".".join([major, minor, patch])

            if m["before"]:
                vs = [vv for vv in all_format_versions if StrictVersion(vv) < StrictVersion(v)]
            else:
                vs = [v]

        vals = map(get_unet2d_nuclei_broad_path, vs)
        if m["package"]:
            vals = map(get_package_from_rdf_path, vals)

        metafunc.parametrize(fixture_name, vals)


@pytest.fixture
def FruNet_model_url():
    return "https://raw.githubusercontent.com/deepimagej/models/master/fru-net_sev_segmentation/model.yaml"
