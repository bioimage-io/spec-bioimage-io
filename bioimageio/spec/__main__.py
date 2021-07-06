import warnings
from pathlib import Path
from pprint import pprint

import typer
from ruamel.yaml import YAML

from bioimageio.spec import load_raw_node

yaml = YAML(typ="safe")

app = typer.Typer()  # https://typer.tiangolo.com/


@app.command()
def package(rdf_source: str, auto_convert: bool = False):
    raise NotImplementedError


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
    """Validate the BioImage.IO Resource Description File (RDF)"""
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
