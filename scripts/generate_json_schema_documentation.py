import shutil
import sys
from pathlib import Path

from json_schema_for_humans.generate import (  # pyright: ignore[reportMissingTypeStubs]
    generate_from_filename,
)
from json_schema_for_humans.generation_configuration import (  # pyright: ignore[reportMissingTypeStubs]
    GenerationConfiguration,
)

from bioimageio.spec import __version__ as spec_version

if __name__ == "__main__":
    schema_file_path = Path("src/bioimageio/spec/static/bioimageio_schema.json")
    if not schema_file_path.exists():
        raise FileNotFoundError(f"JSON schema file not found at '{schema_file_path}'")

    major, minor, path, lib = spec_version.split(".")
    output_dir = Path(f"dist/{schema_file_path.stem}_v{major}-{minor}/")
    latest_dir = Path(f"dist/{schema_file_path.stem}_latest/")
    if output_dir.exists():
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True)

    generate_from_filename(
        schema_file_name=schema_file_path,
        result_file_name=str(output_dir / "index.html"),
        config=GenerationConfiguration(
            link_to_reused_ref=False,
            deprecated_from_description=True,
            default_from_description=True,
            examples_as_yaml=True,
            expand_buttons=True,
            description_is_markdown=True,
            copy_css=True,
            copy_js=True,
        ),
    )

    print(f"Generated json schema docs at {output_dir}", file=sys.stderr)
    _ = shutil.copytree(
        output_dir, latest_dir, copy_function=shutil.copy2, dirs_exist_ok=True
    )
    print(f"Copied generated json schema docs to {latest_dir}", file=sys.stderr)
