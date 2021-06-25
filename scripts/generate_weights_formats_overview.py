import dataclasses
import json
import sys
from argparse import ArgumentParser
from pathlib import Path

from bioimageio.spec import download_uri_to_local_path, raw_nodes, schema
from bioimageio.spec.shared.common import get_args, yaml
from bioimageio.spec.raw_nodes import WeightsFormat

MANIFEST_URL = "https://raw.githubusercontent.com/bioimage-io/bioimage-io-models/gh-pages/manifest.bioimage.io.json"

# defaults for transition period
consumer_defaults = {
    "ilastik": ["pytorch_script", "onnx", "pytorch_state_dict"],
    "zero": ["keras_hdf5"],
    "deepimagej": ["pytorch_script", "tensorflow_saved_model_bundle"],
    "fiji": ["tensorflow_saved_model_bundle"],
    "imjoy": ["onnx"],
}


def parse_args():
    p = ArgumentParser(description=("script that generates weights formats overview"))
    p.add_argument("command", choices=["check", "generate"])

    args = p.parse_args()
    return args


def main(args):
    local = download_uri_to_local_path(MANIFEST_URL)
    with local.open() as f:
        collection = json.load(f)

    collection = collection["collections"]

    consumers = {c["id"]: c for c in collection}

    weights_format_ids = get_args(WeightsFormat)
    weights_format_class_names = [wf.title().replace("_", "") + "WeightsEntry" for wf in weights_format_ids]

    weights_formats = {
        wfcn: {
            "name": getattr(raw_nodes, wfcn).weights_format_name,
            "description": getattr(schema, wfcn).bioimageio_description,
            "consumers": [
                cname
                for cname, c in consumers.items()
                if wf in c.get("supported_weights_formats", consumer_defaults.get(cname, []))
            ],
        }
        for wf, wfcn in zip(weights_format_ids, weights_format_class_names)
    }

    overview = {"consumers": consumers, "weight_formats": weights_formats}  # todo: weight_formats -> weights_formats

    if args.command == "generate":
        with (Path(__file__).parent / "../dist" / "weight_formats_spec.json").open("w") as f:
            json.dump(overview, f, indent=4, sort_keys=True)
    elif args.command == "check":
        with (Path(__file__).parent / "../dist" / "weight_formats_spec.json").open() as f:
            found = json.load(f)

        if found != overview:
            return 1
    else:
        raise NotImplementedError(args.command)


if __name__ == "__main__":
    args = parse_args()
    sys.exit(main(args))
