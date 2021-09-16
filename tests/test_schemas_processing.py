import pytest
from marshmallow import ValidationError
from pytest import raises


class TestPreprocessing:
    class TestZeroMeanUniVarianceKwargs:
        def test_invalid(self):
            from bioimageio.spec.model import schema

            with raises(ValidationError):
                schema.Preprocessing().load({"name": "zero_mean_unit_variance"})

        def test_mode_fixed(self):
            from bioimageio.spec.model import schema

            schema.Preprocessing().load(
                {"name": "zero_mean_unit_variance", "kwargs": {"mode": "fixed", "mean": 1, "std": 2, "axes": "xy"}}
            )
