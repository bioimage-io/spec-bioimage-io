import typing
from copy import deepcopy
from types import ModuleType

import numpy
from marshmallow import RAISE, ValidationError, missing, pre_load, validates, validates_schema

from bioimageio.spec.dataset.v0_2.schema import Dataset as _Dataset
from bioimageio.spec.model.v0_3.schema import (
    KerasHdf5WeightsEntry as KerasHdf5WeightsEntry03,
    OnnxWeightsEntry as OnnxWeightsEntry03,
    Postprocessing as Postprocessing03,
    Preprocessing as Preprocessing03,
    TensorflowJsWeightsEntry as TensorflowJsWeightsEntry03,
    TensorflowSavedModelBundleWeightsEntry as TensorflowSavedModelBundleWeightsEntry03,
    _WeightsEntryBase as _WeightsEntryBase03,
    _common_sha256_hint,
)
from bioimageio.spec.rdf import v0_2 as rdf
from bioimageio.spec.shared import LICENSES, field_validators, fields
from bioimageio.spec.shared.common import get_args, get_args_flat
from bioimageio.spec.shared.schema import ImplicitOutputShape, ParametrizedInputShape, SharedBioImageIOSchema
from . import raw_nodes


# class Dataset(_Dataset):
#     short_bioimageio_description = "in-place definition of [dataset RDF](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/dataset_spec_0_2.md)"


class ModelParent(_BioImageIOSchema):
    id = fields.BioImageIO_ID(resource_type="model")
    uri = fields.Union(
        [fields.URI(), fields.Path()], bioimageio_description="URL or local relative path of a model RDF"
    )
    sha256 = fields.SHA256(bioimageio_description="Hash of the parent model RDF. Note: the hash is not validated")

    @validates_schema
    def id_xor_uri(self, data, **kwargs):
        if ("id" in data) == ("uri" in data):
            raise ValidationError("Either 'id' or 'uri' are required (not both).")


class Model(rdf.schema.RDF):
    @validates("inputs")
    def no_duplicate_input_tensor_names(self, value: typing.List[raw_nodes.InputTensor]):
        if not isinstance(value, list) or not all(isinstance(v, raw_nodes.InputTensor) for v in value):
            raise ValidationError("Could not check for duplicate input tensor names due to another validation error.")

        names = [t.name for t in value]
        if len(names) > len(set(names)):
            raise ValidationError("Duplicate input tensor names are not allowed.")

    license = fields.String(
        validate=field_validators.OneOf(LICENSES),
        required=True,
        bioimageio_description=rdf.schema.RDF.license_bioimageio_description,
    )

    outputs = fields.List(
        fields.Nested(OutputTensor()),
        validate=field_validators.Length(min=1),
        bioimageio_description="Describes the output tensors from this model.",
    )

    @validates("outputs")
    def no_duplicate_output_tensor_names(self, value: typing.List[raw_nodes.OutputTensor]):
        if not isinstance(value, list) or not all(isinstance(v, raw_nodes.OutputTensor) for v in value):
            raise ValidationError("Could not check for duplicate output tensor names due to another validation error.")

        names = [t["name"] if isinstance(t, dict) else t.name for t in value]
        if len(names) > len(set(names)):
            raise ValidationError("Duplicate output tensor names are not allowed.")

    @validates_schema
    def inputs_and_outputs(self, data, **kwargs) -> None:
        ipts: typing.List[raw_nodes.InputTensor] = data.get("inputs")
        outs: typing.List[raw_nodes.OutputTensor] = data.get("outputs")
        if any(
            [
                not isinstance(ipts, list),
                not isinstance(outs, list),
                not all(isinstance(v, raw_nodes.InputTensor) for v in ipts),
                not all(isinstance(v, raw_nodes.OutputTensor) for v in outs),
            ]
        ):
            raise ValidationError("Could not check for duplicate tensor names due to another validation error.")

        # no duplicate tensor names
        names = [t.name for t in ipts + outs]  # type: ignore
        if len(names) > len(set(names)):
            raise ValidationError("Duplicate tensor names are not allowed.")

        tensors_by_name: typing.Dict[str, typing.Union[raw_nodes.InputTensor, raw_nodes.OutputTensor]] = {
            t.name: t for t in ipts + outs  # type: ignore
        }

        # minimum shape leads to valid output:
        # output with subtracted halo has to result in meaningful output even for the minimal input
        # see https://github.com/bioimage-io/spec-bioimage-io/issues/392
        def get_min_shape(t) -> numpy.ndarray:
            if isinstance(t.shape, raw_nodes.ParametrizedInputShape):
                shape = numpy.array(t.shape.min)
            elif isinstance(t.shape, raw_nodes.ImplicitOutputShape):
                scale = list(t.shape.scale)
                ref_shape = get_min_shape(tensors_by_name[t.shape.reference_tensor])

                if any(sc is None for sc in scale):
                    expanded_dims = tuple(idx for idx, sc in enumerate(scale) if sc is None)
                    new_ref_shape = []
                    for idx in range(len(scale)):
                        ref_idx = idx - sum(int(exp < idx) for exp in expanded_dims)
                        new_ref_shape.append(1 if idx in expanded_dims else ref_shape[ref_idx])
                    ref_shape = numpy.array(new_ref_shape)
                    assert len(ref_shape) == len(scale)
                    scale = [0.0 if sc is None else sc for sc in scale]

                offset = numpy.array(t.shape.offset)
                shape = ref_shape * numpy.array(scale) + 2 * offset
            else:
                shape = numpy.array(t.shape)

            return shape

        for out in outs:
            if isinstance(out.shape, raw_nodes.ImplicitOutputShape):
                ndim_ref = len(tensors_by_name[out.shape.reference_tensor].shape)
                ndim_out_ref = len([scale for scale in out.shape.scale if scale is not None])
                if ndim_ref != ndim_out_ref:
                    expanded_dim_note = (
                        f" Note that expanded dimensions (scale: null) are not counted for {out.name}'s dimensionality."
                        if None in out.shape.scale
                        else ""
                    )
                    raise ValidationError(
                        f"Referenced tensor {out.shape.reference_tensor} "
                        f"with {ndim_ref} dimensions does not match "
                        f"output tensor {out.name} with {ndim_out_ref} dimensions.{expanded_dim_note}"
                    )

            min_out_shape = get_min_shape(out)
            if out.halo:
                halo = out.halo
                halo_msg = f" for halo {out.halo}"
            else:
                halo = [0] * len(min_out_shape)
                halo_msg = ""

            if any([s - 2 * h < 1 for s, h in zip(min_out_shape, halo)]):
                raise ValidationError(f"Minimal shape {min_out_shape} of output {out.name} is too small{halo_msg}.")

    parent = fields.Nested(
        ModelParent(),
        bioimageio_description="The model from which this model is derived, e.g. by fine-tuning the weights.",
    )

    run_mode = fields.Nested(
        RunMode(),
        bioimageio_description="Custom run mode for this model: for more complex prediction procedures like test time "
        "data augmentation that currently cannot be expressed in the specification. "
        "No standard run modes are defined yet.",
    )

    sample_inputs = fields.List(
        fields.Union([fields.URI(), fields.Path()]),
        validate=field_validators.Length(min=1),
        bioimageio_description="List of URIs/local relative paths to sample inputs to illustrate possible inputs for "
        "the model, for example stored as png or tif images. "
        "The model is not tested with these sample files that serve to inform a human user about an example use case.",
    )
    sample_outputs = fields.List(
        fields.Union([fields.URI(), fields.Path()]),
        validate=field_validators.Length(min=1),
        bioimageio_description="List of URIs/local relative paths to sample outputs corresponding to the "
        "`sample_inputs`.",
    )

    test_inputs = fields.List(
        fields.Union([fields.URI(), fields.Path()]),
        validate=field_validators.Length(min=1),
        required=True,
        bioimageio_description="List of URIs or local relative paths to test inputs as described in inputs for "
        "**a single test case**. "
        "This means if your model has more than one input, you should provide one URI for each input."
        "Each test input should be a file with a ndarray in "
        "[numpy.lib file format](https://numpy.org/doc/stable/reference/generated/numpy.lib.format.html#module-numpy.lib.format)."
        "The extension must be '.npy'.",
    )
    test_outputs = fields.List(
        fields.Union([fields.URI(), fields.Path()]),
        validate=field_validators.Length(min=1),
        required=True,
        bioimageio_description="Analog to test_inputs.",
    )

    timestamp = fields.DateTime(
        required=True,
        bioimageio_description="Timestamp of the initial creation of this model in [ISO 8601]"
        "(#https://en.wikipedia.org/wiki/ISO_8601) format.",
    )

    training_data = fields.Union([fields.Nested(Dataset()), fields.Nested(LinkedDataset())])

    weights = fields.Dict(
        fields.String(
            validate=field_validators.OneOf(get_args(raw_nodes.WeightsFormat)),
            required=True,
            bioimageio_description="Format of this set of weights. "
            f"One of: {', '.join(get_args(raw_nodes.WeightsFormat))}",
        ),
        fields.Union(
            [fields.Nested(we()) for we in get_args(WeightsEntry)],
            short_bioimageio_description=(
                "The weights for this model. Weights can be given for different formats, but should "
                "otherwise be equivalent. "
                "See [weight_formats_spec_0_4.md]"
                "(https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/weight_formats_spec_0_4.md) "
                "for the required and optional fields per weight format. "
                "The available weight formats determine which consumers can use this model."
            ),
        ),
        required=True,
    )

    @pre_load
    def add_weights_format_key_to_weights_entry_value(self, data: dict, many=False, partial=False, **kwargs):
        data = deepcopy(data)  # Schema.validate() calls pre_load methods, thus we should not modify the input data
        if many or partial:
            raise NotImplementedError

        for weights_format, weights_entry in data.get("weights", {}).items():
            if "weights_format" in weights_entry:
                raise ValidationError(f"Got unexpected key 'weights_format' in weights entry {weights_format}")

            weights_entry["weights_format"] = weights_format

        return data

    @validates_schema
    def validate_reference_tensor_names(self, data, **kwargs) -> None:
        def get_tnames(tname: str):
            return [t.get("name") if isinstance(t, dict) else t.name for t in data.get(tname, [])]

        valid_input_tensor_references = get_tnames("inputs")
        ins = data.get("inputs", [])
        outs = data.get("outputs", [])
        if not isinstance(ins, list) or not isinstance(outs, list):
            raise ValidationError(
                "Failed to validate reference tensor names due to other validation errors in inputs/outputs."
            )

        for t in outs:
            if not isinstance(t, raw_nodes.OutputTensor):
                raise ValidationError("Failed to validate reference tensor names due to validation errors in outputs")

            if t.postprocessing is missing:
                continue

            for postpr in t.postprocessing:
                if postpr.kwargs is missing:
                    continue

                ref_tensor = postpr.kwargs.get("reference_tensor", missing)
                if ref_tensor is not missing and ref_tensor not in valid_input_tensor_references:
                    raise ValidationError(f"{ref_tensor} not found in inputs")

        for t in ins:
            if not isinstance(t, raw_nodes.InputTensor):
                raise ValidationError("Failed to validate reference tensor names due to validation errors in inputs")

            if t.preprocessing is missing:
                continue

            for prep in t.preprocessing:
                if prep.kwargs is missing:
                    continue

                ref_tensor = prep.kwargs.get("reference_tensor", missing)
                if ref_tensor is not missing and ref_tensor not in valid_input_tensor_references:
                    raise ValidationError(f"{ref_tensor} not found in inputs")

                if ref_tensor == t.name:
                    raise ValidationError(f"invalid self reference for preprocessing of tensor {t.name}")

    @validates_schema
    def weights_entries_match_weights_formats(self, data, **kwargs) -> None:
        weights: typing.Dict[str, WeightsEntry] = data.get("weights", {})
        for weights_format, weights_entry in weights.items():
            if not isinstance(weights_entry, get_args(raw_nodes.WeightsEntry)):
                raise ValidationError("Cannot validate keys in weights field due to other validation errors.")

            if weights_format in ["pytorch_state_dict", "torchscript"]:
                if weights_format == "pytorch_state_dict":
                    assert isinstance(weights_entry, raw_nodes.PytorchStateDictWeightsEntry)
                elif weights_format == "torchscript":
                    assert isinstance(weights_entry, raw_nodes.TorchscriptWeightsEntry)
                else:
                    raise NotImplementedError

                if weights_entry.dependencies is missing and weights_entry.pytorch_version is missing:
                    self.warn(f"weights:{weights_format}", "missing 'pytorch_version'")

            if weights_format in ["keras_hdf5", "tensorflow_js", "tensorflow_saved_model_bundle"]:
                if weights_format == "keras_hdf5":
                    assert isinstance(weights_entry, raw_nodes.KerasHdf5WeightsEntry)
                elif weights_format == "tensorflow_js":
                    assert isinstance(weights_entry, raw_nodes.TensorflowJsWeightsEntry)
                elif weights_format == "tensorflow_saved_model_bundle":
                    assert isinstance(weights_entry, raw_nodes.TensorflowSavedModelBundleWeightsEntry)
                else:
                    raise NotImplementedError

                if weights_entry.dependencies is missing and weights_entry.tensorflow_version is missing:
                    self.warn(f"weights:{weights_format}", "missing 'tensorflow_version'")

            if weights_format == "onnx":
                assert isinstance(weights_entry, raw_nodes.OnnxWeightsEntry)
                if weights_entry.dependencies is missing and weights_entry.opset_version is missing:
                    self.warn(f"weights:{weights_format}", "missing 'opset_version'")
