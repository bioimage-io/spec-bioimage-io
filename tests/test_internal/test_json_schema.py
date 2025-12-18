from deepdiff.diff import DeepDiff

from tests.utils import expensive_test


@expensive_test  # test only in developer environment (success is pydantic version dependent)
def test_json_schema_is_up_to_date():
    from bioimageio.spec._internal.json_schema import generate_json_schema
    from bioimageio.spec.utils import get_bioimageio_json_schema

    generated = generate_json_schema()
    existing = get_bioimageio_json_schema()
    diff = DeepDiff(existing, generated)
    assert not diff, diff.pretty()
