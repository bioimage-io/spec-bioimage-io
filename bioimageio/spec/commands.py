import os
import pathlib
import traceback
from pprint import pprint
from typing import IO, Union

from marshmallow import ValidationError

from .io_ import load_raw_resource_description
from .shared import yaml


def validate(
    rdf_source: Union[dict, os.PathLike, IO[str], str],
    update_format: bool = False,
    update_format_inner: bool = None,
    verbose: bool = False,
) -> int:
    """Validate a BioImage.IO Resource Description File (RDF)."""
    if update_format_inner is None:
        update_format_inner = update_format

    source_name = rdf_source.get("name") if isinstance(rdf_source, dict) else rdf_source
    if not isinstance(rdf_source, dict):
        if isinstance(rdf_source, str):
            if rdf_source.startswith("http"):
                from urllib.request import urlretrieve

                rdf_source, response = urlretrieve(rdf_source)
                # todo: check http response code

            try:
                is_path = pathlib.Path(rdf_source).exists()
            except OSError:
                is_path = False

            if is_path:
                rdf_source = pathlib.Path(rdf_source)
            else:
                raise RuntimeError(f"Could not retrieve {rdf_source}")

        if yaml is None:
            raise RuntimeError("Cannot validate from file without ruamel.yaml dependency!")

        rdf_source = yaml.load(rdf_source)

    assert isinstance(rdf_source, dict)
    try:
        raw_rd = load_raw_resource_description(rdf_source, update_to_current_format=update_format)
    except ValidationError as e:
        print(f"Invalid {source_name}:")
        pprint(e.normalized_messages())
        return 1
    except Exception as e:
        print(f"Could not validate {source_name}:")
        pprint(e)
        if verbose:
            traceback.print_exc()

        return 1

    code = 0
    if raw_rd.type == "collection":
        for inner_category in ["application", "collection", "dataset", "model", "notebook"]:
            for inner in getattr(raw_rd, inner_category) or []:
                try:
                    inner_source = inner.source
                except Exception as e:
                    pprint(e)
                    code += 1
                else:
                    code += validate(inner_source, update_format_inner, update_format_inner, verbose)

        if code:
            print(f"Found invalid RDFs in collection {source_name}.")

    if not code:
        print(f"successfully verified {raw_rd.type} {source_name}")

    return code
