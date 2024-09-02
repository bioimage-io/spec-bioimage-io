import json
import sys
from argparse import ArgumentParser
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Dict, Literal, Final

from deepdiff import DeepDiff  # pyright: ignore [reportMissingTypeStubs]
from pydantic import ConfigDict, TypeAdapter
from typing_extensions import assert_never

import bioimageio.spec

MAJOR_MINOR_VERSION: Final[str] = "v" + "-".join(
    bioimageio.spec.__version__.split(".")[0:2]
)


def export_json_schemas_from_type(output: Path, type_: Any, *, title: str):
    adapter = TypeAdapter(
        type_,
        config=ConfigDict(title=title),
    )
    schema = adapter.json_schema()
    write_schema(schema, output)


def write_schema(schema: Dict[str, Any], path: Path):
    with path.open("w") as f:
        json.dump(schema, f, indent=4)

    print(f"written `{path}")


def export_json_schemas(dist: Path):
    assert dist.exists()

    for version in (MAJOR_MINOR_VERSION, "latest"):
        export_json_schemas_from_type(
            dist / f"bioimageio_schema_{version}.json",
            bioimageio.spec.SpecificResourceDescr,
            title=f"bioimage.io resource description {bioimageio.spec.__version__}",
        )


def parse_args():
    p = ArgumentParser(description="script that generates bioimageio json schemas")
    _ = p.add_argument(
        "command", choices=["check", "generate"], nargs="?", default="generate"
    )
    _ = p.add_argument(
        "--dist", nargs="?", default=str((Path(__file__).parent / "../dist").resolve())
    )
    args = p.parse_args()
    return args


def generate_json_schemas(dist: Path, command: Literal["check", "generate"]):
    dist.mkdir(exist_ok=True)
    if command == "generate":
        export_json_schemas(dist)
    elif command == "check":
        existing_schemas = {
            p.name: p for p in Path(dist).glob("bioimageio_schema_*.json")
        }
        with TemporaryDirectory() as tmp_name:
            dist = Path(tmp_name)
            export_json_schemas(dist)
            generated_schemas = {
                p.name: p for p in dist.glob("bioimageio_schema_*.json")
            }
            missing_generated = set(existing_schemas).difference(set(generated_schemas))
            assert not missing_generated, missing_generated
            generated_in_addition = set(existing_schemas).difference(
                set(generated_schemas)
            )
            assert not generated_in_addition, generated_in_addition
            for name, existing_p in existing_schemas.items():
                with existing_p.open() as f:
                    existing = json.load(f)

                with generated_schemas[name].open() as f:
                    generated = json.load(f)

                diff: Any = DeepDiff(existing, generated)
                assert not diff, diff.pretty()
    else:
        assert_never(command)


if __name__ == "__main__":
    args = parse_args()
    sys.exit(generate_json_schemas(Path(args.dist), args.command))
