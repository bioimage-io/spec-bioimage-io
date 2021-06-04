from copy import deepcopy
from pathlib import Path
from pprint import pprint

import requests
import typer
from marshmallow import ValidationError
from ruamel.yaml import YAML

from bioimageio.spec import maybe_convert_model, maybe_convert_manifest, schema

yaml = YAML(typ="safe")

app = typer.Typer()  # https://typer.tiangolo.com/


@app.command()
def verify_spec(model_yaml: Path, auto_convert: bool = False):
    try:
        spec_data = yaml.load(model_yaml)
    except Exception as e:
        pprint(e)
        code = 1
    else:
        try:
            if auto_convert:
                spec_data = maybe_convert_model(deepcopy(spec_data))

            verify_model_data(spec_data)
        except ValidationError as e:
            pprint(e.messages)
            code = 1
        else:
            code = 0
            print(f"successfully verified model {model_yaml}")

    raise typer.Exit(code=code)


def verify_model_data(model_data: dict):
    schema.Model().load(model_data)


def verify_bioimageio_manifest_data(manifest_data: dict, auto_convert: bool = False):
    try:
        if auto_convert:
            manifest_data = maybe_convert_manifest(deepcopy(manifest_data))

        manifest = schema.BioImageIoManifest().load(manifest_data)
    except ValidationError as e:
        pprint(e.messages)
        return 1

    code = 0
    for model in manifest["model"]:
        try:
            response = requests.get(model["source"], stream=True)
            model_data = yaml.load(response.content)
            verify_model_data(model_data)
        except ValidationError as e:
            print("invalid model:", model["source"])
            pprint(e.messages)
            code = 1
        except Exception as e:
            print("invalid model:", model["source"])
            pprint(e)
            code = 1

    return code


@app.command()
def verify_bioimageio_manifest(manifest_yaml: Path, auto_convert: bool = False):
    try:
        manifest_data = yaml.load(manifest_yaml)
    except Exception as e:
        print("invalid manifest", manifest_yaml)
        pprint(e)
        code = 1
    else:
        code = verify_bioimageio_manifest_data(manifest_data, auto_convert=auto_convert)
        if code == 0:
            print(f"successfully verified manifest {manifest_yaml}")

    raise typer.Exit(code=code)


if __name__ == "__main__":
    app()
