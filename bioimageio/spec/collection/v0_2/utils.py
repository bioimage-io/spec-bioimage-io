import os
import pathlib
import warnings
from typing import List, Optional, Tuple, Union

from marshmallow import missing
from marshmallow.utils import _Missing

from . import raw_nodes, schema
from bioimageio.spec.shared.raw_nodes import ResourceDescription as RawResourceDescription


def filter_resource_description(raw_rd: raw_nodes.RDF) -> raw_nodes.RDF:
    return raw_rd


def resolve_collection_entries(
    collection: raw_nodes.Collection, collection_id: Optional[str] = None, update_to_format: Optional[str] = None
) -> List[Tuple[Optional[RawResourceDescription], Optional[str]]]:
    from bioimageio.spec import serialize_raw_resource_description_to_dict, load_raw_resource_description

    if collection.id is missing:
        warnings.warn("Collection has no id; links may not be resolved.")

    ret = []
    seen_ids = set()
    for idx, entry in enumerate(collection.collection):  # type: ignore
        entry_error: Optional[str] = None
        id_info = f"(id={entry.rdf_update['id']}) " if "id" in entry.rdf_update else ""

        # rdf entries are based on collection RDF...
        rdf_data = serialize_raw_resource_description_to_dict(collection)
        assert missing not in rdf_data.values()
        rdf_data.pop("collection")  # ... without the collection field to avoid recursion

        root_id = rdf_data.pop("id", None) if collection_id is None else collection_id
        # update rdf entry with entry's rdf_source
        sub_id: Union[str, _Missing] = missing
        if entry.rdf_source is not missing:
            rdf_source = entry.rdf_source
            if isinstance(rdf_source, str) and not rdf_source.startswith("http") or isinstance(rdf_source, os.PathLike):
                # a relative rdf_source path is relative to collection.root_path
                rdf_source = collection.root_path / pathlib.Path(rdf_source)

            try:
                source_entry_rd = load_raw_resource_description(rdf_source)
            except Exception as e:
                entry_error = f"collection[{idx}]: {id_info}Invalid rdf_source: {e}"
            else:
                source_entry_data = serialize_raw_resource_description_to_dict(source_entry_rd)
                sub_id = source_entry_data.pop("id", missing)
                assert missing not in source_entry_data.values()
                rdf_data.update(source_entry_data)

        # update rdf entry with fields specified directly in the entry
        rdf_update = schema.CollectionEntry().dump(entry)
        assert missing not in rdf_update.values()
        sub_id = rdf_update.pop("id", sub_id)
        if sub_id is missing:
            entry_error = f"collection[{idx}]: Missing `id` field"
        elif sub_id in seen_ids:
            entry_error = f"collection[{idx}]: Duplicate `id` value {sub_id}"
        else:
            seen_ids.add(sub_id)

        rdf = None
        if entry_error is None:
            rdf_data.update(rdf_update)
            if root_id is None:
                rdf_data["id"] = sub_id
            else:
                rdf_data["id"] = f"{root_id}/{sub_id}"

            # Convert simple links to links with collection id prepended
            if "links" in rdf_data:
                for i in range(len(rdf_data["links"])):
                    link = rdf_data["links"][i]
                    if "/" not in link and collection.id is not missing:
                        rdf_data["links"][i] = collection.id + "/" + link

            rdf_data.pop("rdf_source", None)  # remove absorbed rdf_source
            rdf_data["root_path"] = collection.root_path  # collection entry always has the same root as the collection
            assert missing not in rdf_data.values()
            try:
                rdf = load_raw_resource_description(rdf_data, update_to_format=update_to_format)
            except Exception as e:
                entry_error = str(e)

        ret.append((rdf, entry_error))

    return ret
