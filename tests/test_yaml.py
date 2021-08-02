"""
Tests ruamel.yaml replacement.

Why?
PyYAML defaults to YAML 1.1 and does not yet support YAML 1.2 (which is the default for ruamel.yaml atm).
For yaml 1.2 in PyYAML see https://github.com/yaml/pyyaml/issues/116 and  https://github.com/yaml/pyyaml/pull/512 .
We want to ensure compatibility with yaml 1.2, while using yaml 1.1 for now to drop the ruamel.yaml dependency
in order to more easily run with pyodide.
For differences between yaml 1.1 and 1.2, see:
https://yaml.readthedocs.io/en/latest/pyyaml.html#defaulting-to-yaml-1-2-support
"""
import json

from ruamel.yaml import YAML


ruamel_yaml = YAML(typ="safe")


def test_unet2d_nuclei_broad_is_indifferent(unet2d_nuclei_broad_any_path):
    from bioimageio.spec.shared import yaml  # PyYAML replacement for ruamel.yaml

    expected = ruamel_yaml.load(unet2d_nuclei_broad_any_path)
    actual = yaml.load(unet2d_nuclei_broad_any_path)

    # ignore known difference:
    # timestamp contains default utc timezone (tzinfo.utc) for ruamel.yaml, but not for PyYAML
    expected.pop("timestamp")
    actual.pop("timestamp")

    assert expected == actual


def test_flaoting_point_numbers():
    from bioimageio.spec.shared import yaml  # PyYAML replacement for ruamel.yaml

    expected = {"one": 1, "low": 0.000001}
    data_str = json.dumps(expected)
    actual_pyyaml = yaml.load(data_str)
    assert expected == actual_pyyaml

    # just to be sure we test ruamel.yaml as well...
    actual_ruamel = ruamel_yaml.load(data_str)
    assert expected == actual_ruamel
