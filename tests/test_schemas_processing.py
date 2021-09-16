from typing import Union

import pytest
from marshmallow import ValidationError
from pytest import raises


pre_and_post_processing = [
    (True, "zero_mean_unit_variance", {"mode": "fixed", "mean": 1, "std": 2, "axes": "xy"}),
    (False, "zero_mean_unit_variance", {"mode": "unknown", "mean": 1, "std": 2, "axes": "xy"}),
]


@pytest.fixture(
    params=[("Preprocessing", valid, name, kwargs) for valid, name, kwargs in pre_and_post_processing + []]
    + [("Postprocessing", valid, name, kwargs) for valid, name, kwargs in pre_and_post_processing + []]
)
def processing_test_data(request):
    return request.param


def test_processing(processing_test_data):
    proc_class_name, valid, name, kwargs = processing_test_data
    from bioimageio.spec.model import schema

    proc: Union[schema.Preprocessing, schema.Postprocessing] = getattr(schema, proc_class_name)()

    if valid:
        proc.load({"name": name, "kwargs": kwargs})
    else:
        with raises(ValidationError):
            proc.load({"name": name, "kwargs": kwargs})
