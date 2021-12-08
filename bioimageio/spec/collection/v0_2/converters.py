from typing import Any, Dict

from bioimageio.spec.rdf.v0_2.converters import maybe_convert as maybe_convert_rdf


def maybe_convert(data: Dict[str, Any]) -> Dict[str, Any]:
    return maybe_convert_rdf(data)
