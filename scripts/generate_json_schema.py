import json
import sys
from pathlib import Path

from loguru import logger

from bioimageio.spec._internal.json_schema import generate_json_schema

logger.enable("bioimageio")


def main():
    schema = generate_json_schema()
    path = (
        Path(__file__).parent / "../src/bioimageio/spec/static/bioimageio_schema.json"
    )
    with path.open("w") as f:
        json.dump(schema, f, indent=2)

    print(f"written `{path}")


if __name__ == "__main__":
    sys.exit(main())
