from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from bioimageio.spec._internal.io import BioimageioYamlContent
from bioimageio.spec._internal.validation_context import ValidationContext


def test_load_non_existing_rdf():
    from bioimageio.spec import load_description

    spec_path = Path("some/none/existing/path/to/spec.model.yaml")

    with pytest.raises(FileNotFoundError):
        _ = load_description(spec_path)


@pytest.mark.parametrize(
    "rid",
    [
        "invigorating-lab-coat",
        "invigorating-lab-coat/1",
        "10.5281/zenodo.11092896",  # backup doi of version 1
        "10.5281/zenodo.11092895",  # concept doi of backup
    ],
)
def test_load_by_id(rid: str):
    from bioimageio.spec._internal.io_utils import open_bioimageio_yaml

    rdf = open_bioimageio_yaml(rid).content
    assert rdf["id"] == "invigorating-lab-coat"


def test_load_description_again(unet2d_data: BioimageioYamlContent):
    from bioimageio.spec import build_description, load_description

    descr = build_description(
        unet2d_data, context=ValidationContext(perform_io_checks=False)
    )
    descr2 = load_description(  # pyright: ignore[reportUnknownVariableType,reportCallIssue]
        descr,
        perform_io_checks=False,
    )
    assert descr is descr2


def test_load_description_forwards_pbar(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    import bioimageio.spec._io as io_module
    from bioimageio.spec import load_description

    seen_source: list[object] = []
    seen_kwargs: dict[str, object] = {}
    expected = object()

    def fake_open_bioimageio_yaml(source: object, /, **kwargs: object):
        seen_source.append(source)
        seen_kwargs.update(kwargs)
        return SimpleNamespace(
            content={"type": "dataset", "format_version": "0.3.0"},
            original_root=tmp_path,
            original_file_name="bioimageio.yaml",
            original_source_name="mock-source",
        )

    seen_context: list[object] = []

    def fake_build_description(
        content: object, /, *, context: object, format_version: object
    ):
        seen_context.append(context)
        return expected

    monkeypatch.setattr(io_module, "open_bioimageio_yaml", fake_open_bioimageio_yaml)
    monkeypatch.setattr(io_module, "build_description", fake_build_description)

    result = load_description(tmp_path / "bioimageio.yaml", progressbar=False)

    assert result is expected
    assert seen_source == [tmp_path / "bioimageio.yaml"]
    assert seen_kwargs["progressbar"] is False
    assert seen_kwargs["sha256"] is None
    assert getattr(seen_context[0], "progressbar", "missing") is False


def test_open_bioimageio_yaml_forwards_progressbar_to_reader(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    from bioimageio.spec._internal import io_utils

    seen_source: list[object] = []
    seen_kwargs: dict[str, object] = {}

    class Reader:
        is_zipfile = False

        def read(self) -> bytes:
            return b"type: dataset\nformat_version: 0.3.0\n"

    def fake_get_reader(source: object, /, **kwargs: object) -> Reader:
        seen_source.append(source)
        seen_kwargs.update(kwargs)
        return Reader()

    monkeypatch.setattr(io_utils, "get_reader", fake_get_reader)

    source = tmp_path / "bioimageio.yaml"
    opened = io_utils.open_bioimageio_yaml(source, progressbar=False)

    assert opened.content == {"type": "dataset", "format_version": "0.3.0"}
    assert seen_source == [source]
    assert seen_kwargs["progressbar"] is False


def test_open_bioimageio_yaml_forwards_progressbar_to_id_map_entry(
    monkeypatch: pytest.MonkeyPatch,
):
    from bioimageio.spec._internal import io_utils

    seen_progressbar: list[Any] = []

    class Reader:
        is_zipfile = False

        def read(self) -> bytes:
            return b"type: dataset\nformat_version: 0.3.0\n"

    class Entry:
        source = "https://example.com/bioimageio.yaml"

        def get_reader(self, *, progressbar: Any = None) -> Reader:
            seen_progressbar.append(progressbar)
            return Reader()

    def fake_interprete_file_source(source: Any) -> Any:
        raise FileNotFoundError(source)

    monkeypatch.setattr(io_utils, "interprete_file_source", fake_interprete_file_source)
    monkeypatch.setattr(io_utils, "get_id_map", lambda: {"collection-id": Entry()})

    opened = io_utils.open_bioimageio_yaml("collection-id", progressbar=False)

    assert opened.content == {"type": "dataset", "format_version": "0.3.0"}
    assert seen_progressbar == [False]


def test_load_dataset_description(covid_if_dataset_path: Path, tmp_path: Path):
    from bioimageio.spec import load_dataset_description
    from bioimageio.spec._io import save_bioimageio_yaml_only
    from bioimageio.spec.dataset.v0_2 import DatasetDescr

    dataset_descr = load_dataset_description(covid_if_dataset_path)
    assert isinstance(dataset_descr, DatasetDescr)

    # this example happens to consist only of the bioimageio.yaml file,
    # so we can test the roundtrip with `save_bioimageio_yaml_only`
    save_bioimageio_yaml_only(dataset_descr, tmp_path / "dataset.yaml")
    dataset_descr2 = load_dataset_description(tmp_path / "dataset.yaml")
    assert isinstance(dataset_descr2, DatasetDescr)  # we cannot expect
    assert dataset_descr.model_dump(mode="json") == dataset_descr2.model_dump(
        mode="json"
    )
