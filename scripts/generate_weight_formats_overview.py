import dataclasses
import json
import sys
from pathlib import Path

from bioimageio.spec import download_uri_to_local_path, schema
from bioimageio.spec.shared.common import get_args, yaml
from bioimageio.spec.raw_nodes import WeightsEntry

MANIFEST_URL = "https://raw.githubusercontent.com/bioimage-io/bioimage-io-models/gh-pages/manifest.bioimage.io.json"

# defaults for transition period
consumer_defaults = {
    "ilastik": ["pytorch_script", "onnx", "pytorch_state_dict"],
    "zero": ["keras_hdf5"],
    "deepimagej": ["pytorch_script", "tensorflow_saved_model_bundle"],
    "fiji": ["tensorflow_saved_model_bundle"],
    "imjoy": ["onnx"],
}


def main():
    local = download_uri_to_local_path(MANIFEST_URL)
    with local.open() as f:
        collection = json.load(f)

    collection = collection["collections"]

    consumers = {c["id"]: c for c in collection}

    def get_weights_format_from_entry_class(entry_class):
        for field in dataclasses.fields(entry_class):
            if field.name == "weights_format":
                return get_args(field.type)[0]

        raise NotImplementedError(entry_class)

    weights_formats = {
        get_weights_format_from_entry_class(entry): {
            "name": entry.weights_format_name,
            "description": getattr(schema, entry.__name__).bioimageio_description,
            "consumers": [
                cname
                for cname, c in consumers.items()
                if get_weights_format_from_entry_class(entry)
                in c.get("supported_weights_formats", consumer_defaults.get(cname, []))
            ],
        }
        for entry in get_args(WeightsEntry)
    }

    overview = {"consumers": consumers, "weight_formats": weights_formats}  # todo: weight_formats -> weights_formats

    with (Path(__file__).parent / "../dist" / "weight_formats_spec.json").open("w") as f:
        json.dump(overview, f, indent=4, sort_keys=True)


if __name__ == "__main__":
    sys.exit(main())
