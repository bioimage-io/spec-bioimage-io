import json

from deepdiff.diff import DeepDiff


def test_json_schema_is_up_to_date():
    from bioimageio.spec._internal.json_schema import generate_json_schema
    from bioimageio.spec.utils import get_bioimageio_json_schema

    generated = generate_json_schema()
    # encode and decode with json for exact match, e.g. json turns int into float
    generated_json_roundtrip = json.loads(json.dumps(generated))

    existing = get_bioimageio_json_schema()
    diff = DeepDiff(existing, generated_json_roundtrip)
    assert not diff, diff.pretty()
