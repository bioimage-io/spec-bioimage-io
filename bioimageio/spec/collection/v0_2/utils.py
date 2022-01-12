from typing import List, Optional, Tuple, Union

from marshmallow import missing
from marshmallow.utils import _Missing

from . import raw_nodes


def filter_resource_description(raw_rd: raw_nodes.RDF) -> raw_nodes.RDF:
    return raw_rd


def resolve_collection_entries(raw_rd: raw_nodes.Collection) -> List[Tuple[dict, Optional[str]]]:
    from bioimageio.spec import serialize_raw_resource_description_to_dict
    from bioimageio.spec.shared.utils import resolve_rdf_source

    ret = []
    seen_ids = set()
    for idx, entry in enumerate(raw_rd.collection):  # type: ignore
        entry_error: Optional[str] = None
        id_info = f"(id={entry.rdf_update['id']}) " if "id" in entry.rdf_update else ""

        # rdf entries are based on collection RDF...
        rdf_data = serialize_raw_resource_description_to_dict(raw_rd)
        rdf_data.pop("collection")  # ... without the collection field to avoid recursion

        root_id = rdf_data.pop("id", missing)
        # update rdf entry with entry's rdf_source
        sub_id: Union[str, _Missing] = missing
        if entry.rdf_source is not missing:
            try:
                remote_rdf_update, _, _ = resolve_rdf_source(entry.rdf_source)
            except Exception as e:
                entry_error = f"collection[{idx}]: {id_info}Invalid rdf_source: {e}"
            else:
                sub_id = remote_rdf_update.pop("id", missing)
                rdf_data.update(remote_rdf_update)

        # update rdf entry with fields specified directly in the entry
        rdf_update = dict(entry.rdf_update)
        sub_id = rdf_update.pop("id", sub_id)
        if sub_id is missing:
            entry_error = f"collection[{idx}]: Missing `id` field"
        elif sub_id in seen_ids:
            entry_error = f"collection[{idx}]: Duplicate `id` value {sub_id}"
        else:
            seen_ids.add(sub_id)

        rdf_data.update(rdf_update)
        rdf_data["id"] = f"{root_id}/{sub_id}"
        ret.append((rdf_data, entry_error))

    return ret
