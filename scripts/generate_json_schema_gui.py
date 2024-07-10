import sys
import bioimageio.spec
import tempfile
import os
from pathlib import Path
import shutil
from scripts.generate_json_schemas import MAJOR_MINOR_VERSION, export_json_schemas_from_type

from json_schema_for_humans.generate import generate_from_filename # pyright: ignore [reportMissingTypeStubs]
from json_schema_for_humans.generation_configuration import GenerationConfiguration # pyright: ignore [reportMissingTypeStubs]

if __name__ == "__main__":
    schema_file_handle, schema_file_path = tempfile.mkstemp()
    os.close(schema_file_handle)

    export_json_schemas_from_type(
        output=Path(schema_file_path),
        type_=bioimageio.spec.SpecificResourceDescr,
        title="Model Description"
    )

    output_dir = Path(__file__).parent.parent / f"dist/json_schema_gui_{MAJOR_MINOR_VERSION}"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    generate_from_filename(
        schema_file_name=schema_file_path,
        result_file_name=str(output_dir.joinpath("index.html")),
        config=GenerationConfiguration(
            # link_to_reused_ref=False,
            deprecated_from_description=True,
            default_from_description=True,
            examples_as_yaml=True,
            expand_buttons=True,
            description_is_markdown=True,
            copy_css=True,
            copy_js=True,
        )
    )

    print(f"Generated json schema docs at {output_dir}", file=sys.stderr)

# Your doc is now in a file named "schema_doc.html". Next to it, "schema_doc.min.js" was copied, but not "schema_doc.css"
# Your doc will contain a "Expand all" and a "Collapse all" button at the top
