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
def verify(rdf_source: str, auto_convert: bool = False, auto_convert_inner: bool = None):
    if auto_convert_inner is None:
        auto_convert_inner = auto_convert

    raise typer.Exit(code=_verify(rdf_source, auto_convert, auto_convert_inner))


def _verify(rdf_source: str, auto_convert: bool, auto_convert_inner: bool) -> int:
    try:
        raw_node = load_raw_node(rdf_source, update_to_current_format=auto_convert)
    except Exception as e:
        print(f"Could not verify {rdf_source}:")
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
                        ret += _verify(inner_source, auto_convert_inner, auto_convert_inner)

        return ret


@app.command()
def verify_spec(model_yaml: str, auto_convert: bool = False):
    warnings.warn("'verify_spec' is deprecated in favor of 'verify'")
    return verify(model_yaml, auto_convert)


@app.command()
def verify_bioimageio_manifest(manifest_yaml: Path, auto_convert: bool = False):
    warnings.warn("'verify_bioimageio_manifest' is deprecated in favor of 'verify'")
    return verify(manifest_yaml.absolute().as_uri(), auto_convert)


if __name__ == "__main__":
    app()
