import shutil
import traceback
from pathlib import Path
from pprint import pprint
from typing import List, Optional, Union

from marshmallow import ValidationError

from bioimageio.spec import export_package, load_raw_node
from bioimageio.spec.shared.raw_nodes import URI
from bioimageio.spec.shared.utils import resolve_uri


def package(
    rdf_source: Union[Path, str, URI, dict],
    path: Path = Path() / "{src_name}-package.zip",
    update_format: bool = False,
    weights_priority_order: Optional[List[str]] = None,
    verbose: bool = False,
) -> int:
    """Package a BioImage.IO resource described by a BioImage.IO Resource Description File (RDF)."""
    code = validate(rdf_source, update_format=update_format, update_format_inner=update_format, verbose=verbose)
    source_name = rdf_source.get("name") if isinstance(rdf_source, dict) else rdf_source
    if code:
        print(f"Cannot export invalid BioImage.IO RDF {source_name}")
        return code

    try:
        tmp_package_path = export_package(
            rdf_source, update_to_current_format=update_format, weights_priority_order=weights_priority_order
        )
    except Exception as e:
        print(f"Failed to package {source_name} due to: {e}")
        if verbose:
            traceback.print_exc()
        return 1

    try:
        rdf_local_source = resolve_uri(rdf_source)
        path = path.with_name(path.name.format(src_name=rdf_local_source.stem))
        shutil.move(tmp_package_path, path)
    except Exception as e:
        print(f"Failed to move package from {tmp_package_path} to {path} due to: {e}")
        if verbose:
            traceback.print_exc()
        return 1

    print(f"exported bioimageio package from {source_name} to {path}")
    return 0


def validate(
    rdf_source: Union[Path, str, URI, dict],
    update_format: bool = False,
    update_format_inner: bool = None,
    verbose: bool = False,
) -> int:
    """Validate a BioImage.IO Resource Description File (RDF)."""
    if update_format_inner is None:
        update_format_inner = update_format

    source_name = rdf_source.get("name") if isinstance(rdf_source, dict) else rdf_source
    try:
        raw_node = load_raw_node(rdf_source, update_to_current_format=update_format)
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
    if raw_node.type == "collection":
        for inner_category in ["application", "collection", "dataset", "model", "notebook"]:
            for inner in getattr(raw_node, inner_category) or []:
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
        print(f"successfully verified {raw_node.type} {source_name}")

    return code
