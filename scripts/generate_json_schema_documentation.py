import shutil
import sys
from pathlib import Path

from json_schema_for_humans.generate import generate_from_filename
from json_schema_for_humans.generation_configuration import GenerationConfiguration

if __name__ == "__main__":
    glob_pattern = "dist/bioimageio_schema_*.json"
    schema_paths = list(Path().glob(glob_pattern))
    if not schema_paths:
        raise FileNotFoundError(
            f"no json schema files found with pattern '{glob_pattern}'"
        )

    for schema_file_path in schema_paths:
        output_dir = Path() / f"dist/{schema_file_path.stem}"
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
