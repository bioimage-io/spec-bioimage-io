from typing import List, Optional, Tuple, Union

from marshmallow import missing
from marshmallow.utils import _Missing

from . import raw_nodes, schema


def filter_resource_description(raw_rd: raw_nodes.RDF) -> raw_nodes.RDF:
    return raw_rd


def resolve_collection_entries(
    collection: raw_nodes.Collection, collection_id: Optional[str] = None
) -> List[Tuple[dict, Optional[str]]]:
    from bioimageio.spec import serialize_raw_resource_description_to_dict
    from bioimageio.spec.shared.utils import resolve_rdf_source

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
            try:
                remote_rdf_update, _, _ = resolve_rdf_source(entry.rdf_source)
            except Exception as e:
                entry_error = f"collection[{idx}]: {id_info}Invalid rdf_source: {e}"
            else:
                sub_id = remote_rdf_update.pop("id", missing)
                assert missing not in remote_rdf_update.values()
                rdf_data.update(remote_rdf_update)

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

        rdf_data.update(rdf_update)
        if root_id is None:
            rdf_data["id"] = sub_id
        else:
            rdf_data["id"] = f"{root_id}/{sub_id}"

        rdf_data.pop("rdf_source", None)  # remove rdf_source as we return a plain dict that has no simple source file
        assert missing not in rdf_data.values()
        ret.append((rdf_data, entry_error))

    return ret
