import json
import pathlib

with (pathlib.Path(__file__).parent / "VERSION").open() as f:
    __version__ = json.load(f)["version"]
