import shutil
from pathlib import Path
from pprint import pprint
from typing import List, Optional, Union

from bioimageio.spec import export_package, load_raw_node
from bioimageio.spec.shared.raw_nodes import URI
from bioimageio.spec.shared.utils import resolve_uri


def package(
    rdf_source: Union[Path, str, URI, dict],
    path: Path = Path() / "{src_name}-package.zip",
    update_format: bool = False,
    weights_priority_order: Optional[List[str]] = None,
) -> int:
    """Package a BioImage.IO resource described by a BioImage.IO Resource Description File (RDF)."""
    code = validate(rdf_source, update_format=update_format, update_format_inner=update_format)
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

    return code


def validate(
    rdf_source: Union[Path, str, URI, dict], update_format: bool = False, update_format_inner: bool = None
) -> int:
    """Validate a BioImage.IO Resource Description File (RDF)."""
    if update_format_inner is None:
        update_format_inner = update_format

    try:
        raw_node = load_raw_node(rdf_source, update_to_current_format=update_format)
    except Exception as e:
        print(f"Could not validate {rdf_source}:")
        pprint(e)
        code = 1
    else:
        code = 0
        print(f"successfully verified {raw_node.type} {rdf_source}")
        if raw_node.type == "collection":
            for inner_category in ["application", "collection", "dataset", "model", "notebook"]:
                for inner in getattr(raw_node, inner_category) or []:
                    try:
                        inner_source = inner.source
                    except Exception as e:
                        pprint(e)
                        code += 1
                    else:
                        code += validate(inner_source, update_format_inner, update_format_inner)

    return code
