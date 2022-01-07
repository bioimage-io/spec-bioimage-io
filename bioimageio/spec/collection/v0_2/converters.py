from typing import Any, Dict

from bioimageio.spec.rdf.v0_2.converters import maybe_convert as maybe_convert_rdf


def maybe_convert(data: Dict[str, Any]) -> Dict[str, Any]:
    if data.get("format_version") in ("0.2.0", "0.2.1"):
        # move all type groups to the 'collection' field
        if "collection" not in data:
            data["collection"] = []
        for group in ["application", "model", "dataset", "notebook"]:
            if group in data:
                data["collection"] += data[group]

        data["format_version"] = "0.2.2"

    return maybe_convert_rdf(data)
