import shutil
import warnings
from pathlib import Path
from pprint import pprint
from typing import List, Optional

import typer
from ruamel.yaml import YAML

from bioimageio.spec import export_package, load_raw_node
from bioimageio.spec.shared.utils import resolve_uri

yaml = YAML(typ="safe")

app = typer.Typer()  # https://typer.tiangolo.com/


@app.command()
def package(
    rdf_source: str = typer.Argument(..., help="RDF source as relative file path or URI"),
    path: Path = typer.Argument(Path() / "{src_name}-package.zip", help="Save package as"),
    update_format: bool = typer.Option(
        False,
        help="Update format version to the latest version (might fail even if source adheres to an old format version). "
        "To inform the format update the source may specify fields of future versions in "
        "config:future:<future version>.",  # todo: add future documentation
    ),
    weights_priority_order: Optional[List[str]] = typer.Option(
        None,
        "-wpo",
        help="For model packages only. "
        "If given only the first matching weights format present in the model is included. "
        "Defaults to include all weights present in source.",
        show_default=False,
    ),
):
    """Package a BioImage.IO resource described by a BioImage.IO Resource Description File (RDF)."""
    code = _validate(rdf_source, update_format=update_format, update_format_inner=update_format)
    if code:
        print(f"Cannot export invalid BioImage.IO RDF {rdf_source}")
    else:
        try:
            tmp_package_path = export_package(
                rdf_source, update_to_current_format=update_format, weights_priority_order=weights_priority_order
            )
        except Exception as e:
            print(f"Failed to package {rdf_source} due to: {e}")
            code = 1
        else:
            try:
                rdf_local_source = resolve_uri(rdf_source)
                path = path.with_name(path.name.format(src_name=rdf_local_source.stem))
                shutil.move(tmp_package_path, path)
            except Exception as e:
                print(f"Failed to move package from {tmp_package_path} to {path} due to: {e}")
                code = 1

        if not code:
            print(f"exported bioimageio package from {rdf_source} to {path}")

    raise typer.Exit(code=code)


@app.command()
def validate(
    rdf_source: str = typer.Argument(..., help="RDF source as relative file path or URI"),
    update_format: bool = typer.Option(
        False,
        help="Update format version to the latest (might fail even if source adheres to an old format version). "
        "To inform the format update the source may specify fields of future versions in "
        "config:future:<future version>.",  # todo: add future documentation
    ),
    update_format_inner: bool = typer.Option(
        None, help="For collection RDFs only. Defaults to value of 'update-format'."
    ),
):
    """Validate a BioImage.IO Resource Description File (RDF)."""
    if update_format_inner is None:
        update_format_inner = update_format

    raise typer.Exit(code=_validate(rdf_source, update_format, update_format_inner))


def _validate(rdf_source: str, update_format: bool, update_format_inner: bool) -> int:
    try:
        raw_node = load_raw_node(rdf_source, update_to_current_format=update_format)
    except Exception as e:
        print(f"Could not validate {rdf_source}:")
        pprint(e)
        return 1
    else:
        ret = 0
        print(f"successfully verified {raw_node.type} {rdf_source}")
        if raw_node.type == "collection":
            for inner_category in ["application", "collection", "dataset", "model", "notebook"]:
                for inner in getattr(raw_node, inner_category) or []:
                    try:
                        inner_source = inner.source
                    except Exception as e:
                        pprint(e)
                        ret += 1
                    else:
                        ret += _validate(inner_source, update_format_inner, update_format_inner)

        return ret


@app.command()
def verify_spec(model_yaml: str, auto_convert: bool = False):
    """'verify-spec' is deprecated in favor of 'validate'"""
    warnings.warn("'verify_spec' is deprecated in favor of 'validate'")
    return validate(model_yaml, auto_convert)


@app.command()
def verify_bioimageio_manifest(manifest_yaml: Path, auto_convert: bool = False):
    """'verify-bioimageio-manifest' is deprecated in favor of 'validate'"""
    warnings.warn("'verify_bioimageio_manifest' is deprecated in favor of 'validate'")
    return validate(manifest_yaml.absolute().as_uri(), auto_convert)


if __name__ == "__main__":
    app()
