import json
import sys
from argparse import ArgumentParser
from pathlib import Path

from marshmallow_jsonschema import JSONSchema

import bioimageio.spec

from bioimageio.spec.shared.common import ruamel_yaml, pyyaml_yaml

if ruamel_yaml is None:
    raise RuntimeError("Cannot compare yaml syntax without the ruamel.yaml package")


def parse_args():
    p = ArgumentParser(
        description="Check for differences between yaml 1.1 (using PyYAML) and yaml 1.2 syntax (using ruamel.yaml)."
    )
    p.add_argument("resource_description_path", type=Path)
    args = p.parse_args()
    return args


def main(resource_description_path: Path):

    pyyaml = pyyaml_yaml.load(resource_description_path)
    assert isinstance(pyyaml, dict)
    ruamel = ruamel_yaml.load(resource_description_path)
    assert isinstance(ruamel, dict)

    diff = {key: (value, ruamel[key]) for key, value in pyyaml.items() if value != ruamel[key]}
    if diff:
        print(f"Found differences between yaml syntax 1.1/1.2 for {resource_description_path}:")
        print(diff)
    else:
        print(f"No differences found between yaml syntax 1.1/1.2 for {resource_description_path}:")

    return len(diff)


if __name__ == "__main__":
    args = parse_args()
    sys.exit(main(args.resource_description_path))
