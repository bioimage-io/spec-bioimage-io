from bioimageio.spec.utils.maybe_convert_to_v0_3 import maybe_convert_model_to_v0_3


def maybe_convert_model(data):
    data = maybe_convert_model_to_v0_3(data)

    # remove 'future' from config if no other than the used future entries exist
    config = data.get("config", {})
    if config.get("future") == {}:
        del config["future"]

    return data


def maybe_convert_manifest(data):
    if "model" in data:
        data["model"] = [maybe_convert_model(m) for m in data["model"]]

    return data
