import json
import sys
from pathlib import Path

from bioimageio.spec._description import DESCRIPTIONS_MAP
from bioimageio.spec._internal.json_schema import generate_json_schema


def main():
    for typ, format_versions_map in DESCRIPTIONS_MAP.items():
        if typ is None:
            continue

        for format_version in format_versions_map.keys():
            schema = generate_json_schema(type_format=(typ, format_version))
            path = Path(f"dist/bioimageio_schema_{typ}_{format_version}.json")
            with path.open("w") as f:
                json.dump(schema, f, indent=2)

            print(f"written `{path}`")


if __name__ == "__main__":
    sys.exit(main())
