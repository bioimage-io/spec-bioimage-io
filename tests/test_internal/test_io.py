from pathlib import Path, PurePath
from typing import Any

import pytest
from pydantic import ValidationError

from bioimageio.spec import ValidationContext
from bioimageio.spec.common import RelativeFilePath


@pytest.mark.parametrize("p", [PurePath("maybe_a_file"), "maybe_a_file"])
def test_valid_relative_file_path(p: Any):
    from bioimageio.spec._internal.io import RelativeFilePath

    with ValidationContext(perform_io_checks=False):
        _ = RelativeFilePath(p)


@pytest.mark.parametrize(
    "p",
    [
        PurePath(),
        PurePath(""),
        PurePath("."),
        PurePath("http://example.cm"),
        PurePath("https://example.com"),
    ],
)
def test_invalid_relative_file_path(p: Any):
    from bioimageio.spec._internal.io import RelativeFilePath

    with ValidationContext(perform_io_checks=False), pytest.raises(ValidationError):
        _ = RelativeFilePath(p)


@pytest.mark.parametrize(
    "p",
    [
        PurePath(__file__).parent,
    ],
)
def test_invalid_relative_file_path_io_check(p: Any):
    from bioimageio.spec._internal.io import RelativeFilePath

    with ValidationContext(perform_io_checks=True), pytest.raises(ValidationError):
        _ = RelativeFilePath(p)


def test_interprete_file_source_from_str():
    from bioimageio.spec._internal.io import interprete_file_source

    src = f"{PurePath(__file__).parent.name}/{PurePath(__file__).name}"

    with ValidationContext(root=Path(__file__).parent.parent):
        interpreted = interprete_file_source(src)
        assert isinstance(interpreted, RelativeFilePath)
        assert isinstance(interpreted.absolute(), Path)
        assert interpreted.absolute().exists()


def test_interprete_file_source_from_rel_path():
    from bioimageio.spec._internal.io import interprete_file_source

    with ValidationContext(root=Path(__file__).parent.parent):
        src = RelativeFilePath(
            PurePath(PurePath(__file__).parent.name) / PurePath(__file__).name
        )

    interpreted = interprete_file_source(src)
    assert isinstance(interpreted, RelativeFilePath)
    assert isinstance(interpreted.absolute(), Path)
    assert interpreted.absolute().exists()


def test_known_files(tmp_path: Path):
    from bioimageio.spec._internal.io import FileDescr, get_sha256

    file_name = "lala.txt"
    src = tmp_path / file_name
    _ = src.write_text("lala")
    sha = get_sha256(src)

    with ValidationContext(root=tmp_path, perform_io_checks=True):
        # set sha on loading
        file_descr = FileDescr(source=file_name)  # pyright: ignore[reportArgumentType]
        assert file_descr.sha256 == sha

        # validate given sha
        file_descr = FileDescr(
            source=file_name, sha256=sha  #  pyright: ignore[reportArgumentType]
        )
        assert file_descr.sha256 == sha

    # give known files to bypass file io
    with ValidationContext(known_files={file_name: sha}, perform_io_checks=True):
        # set sha on loading
        file_descr = FileDescr(source=file_name)  # pyright: ignore[reportArgumentType]
        assert file_descr.sha256 == sha

        # validate given sha
        file_descr = FileDescr(
            source=file_name, sha256=sha  # pyright: ignore[reportArgumentType]
        )
        assert file_descr.sha256 == sha
