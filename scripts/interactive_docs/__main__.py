import sys
from pathlib import Path

from typing_extensions import assert_never

from bioimageio.spec import SpecificResourceDescr
from scripts.generate_json_schemas import MAJOR_MINOR_VERSION

from . import generate_docs

html_result: "str | Exception" = generate_docs(
    raw_type=SpecificResourceDescr, root_path=["Delivery"]
)
if isinstance(html_result, Exception):
    print(f"Could not generate docs: {html_result}", file=sys.stderr)
    exit(1)
elif isinstance(html_result, str):
    docs_output_path = (
        Path(__file__).parent.parent.parent
        / f"dist/interactive_docs_{MAJOR_MINOR_VERSION}.html"
    )
    docs_output_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Writing interactive docs to {docs_output_path}")
    with open(docs_output_path, "w", encoding="utf-8") as f:
        _ = f.write(html_result)
        print(f"Wrote {_} bytes to {docs_output_path}")
else:
    assert_never(html_result)
