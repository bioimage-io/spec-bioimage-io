from typing import Union

import pytest
from marshmallow import ValidationError
from pytest import raises


pre_and_post_processing = [
    (True, "binarize", {"threshold": 0.5}),
    (False, "binarize", {"mode": "fixed", "threshold": 0.5}),
    (True, "clip", {"min": 0.2, "max": 0.5}),
    (False, "clip", {"min": "min", "max": 0.5}),
    (True, "scale_linear", {"gain": 2, "offset": 0.5, "axes": "xy"}),
    (False, "scale_linear", {"gain": 2, "offset": 0.5, "axes": "b"}),
    (True, "sigmoid", {}),
    (False, "sigmoid", {"axes": "x"}),
    (True, "zero_mean_unit_variance", {"mode": "fixed", "mean": 1, "std": 2, "axes": "xy"}),
    (False, "zero_mean_unit_variance", {"mode": "unknown", "mean": 1, "std": 2, "axes": "xy"}),
    (True, "scale_range", {"mode": "per_sample", "axes": "xy"}),
    (False, "scale_range", {"mode": "fixed", "axes": "xy"}),
    (True, "scale_range", {"mode": "per_sample", "axes": "xy", "min_percentile": 5, "max_percentile": 50}),
    (False, "scale_range", {"mode": "per_sample", "axes": "xy", "min_percentile": 50, "max_percentile": 50}),
    (False, "scale_range", {"mode": "per_sample", "axes": "xy", "min": 0}),
]


@pytest.fixture(
    params=[
        ("Preprocessing", valid, name, kwargs)
        for valid, name, kwargs in pre_and_post_processing
        + [(False, "scale_range", {"mode": "per_dataset", "axes": "xy", "reference_tensor": "some_input_tensor_name"})]
    ]
    + [
        ("Postprocessing", valid, name, kwargs)
        for valid, name, kwargs in pre_and_post_processing
        + [
            (True, "scale_range", {"mode": "per_sample", "axes": "xy"}),
            (True, "scale_range", {"mode": "per_dataset", "axes": "xy", "reference_tensor": "some_input_tensor_name"}),
            (True, "scale_mean_variance", {"mode": "per_sample", "reference_tensor": "some_tensor_name"}),
            (False, "scale_mean_variance", {"mode": "per_sample"}),
            (True, "scale_mean_variance", {"mode": "per_dataset", "reference_tensor": "some_tensor_name"}),
            (False, "scale_mean_variance", {"mode": "per_dataset"}),
        ]
    ]
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
