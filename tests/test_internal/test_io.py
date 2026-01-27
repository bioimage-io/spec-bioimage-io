import io
from pathlib import Path, PurePath
from typing import Annotated, Any, Union
from zipfile import ZipFile

import h5py
import httpx
import pytest
from pydantic import Field, ValidationError
from respx import MockRouter

from bioimageio.spec import ValidationContext
from bioimageio.spec._internal.io_basics import Sha256, ZipPath
from bioimageio.spec._internal.url import HttpUrl
from bioimageio.spec._internal.validation_context import get_validation_context
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


def test_file_descr_with_data_path(tmp_path: Path):
    from bioimageio.spec._internal.io import FileDescr

    with h5py.File(tmp_path / "data.h5", "w") as f:
        _ = f.create_dataset("my_dataset", data=[1, 2, 3])

    with get_validation_context().replace(perform_io_checks=True):
        fdescr = FileDescr(source=f"{tmp_path / 'data.h5'}/my_dataset")

    assert isinstance(fdescr.source, Path)
    assert fdescr.surce.name == "data.h5/my_dataset"


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
            source=file_name,  #  pyright: ignore[reportArgumentType]
            sha256=sha,
        )
        assert file_descr.sha256 == sha

    # give known files to bypass file io
    with ValidationContext(known_files={file_name: sha}, perform_io_checks=True):
        # set sha on loading
        file_descr = FileDescr(source=file_name)  # pyright: ignore[reportArgumentType]
        assert file_descr.sha256 == sha

        # validate given sha
        file_descr = FileDescr(
            source=file_name,  # pyright: ignore[reportArgumentType]
            sha256=sha,
        )
        assert file_descr.sha256 == sha


def test_disable_cache(respx_mock: MockRouter):
    from bioimageio.spec._internal.io import get_reader
    from bioimageio.spec._internal.url import RootHttpUrl

    url = "https://mock_example.com/files/my_bioimageio.yaml"
    route = respx_mock.get(url).mock(
        httpx.Response(text="example content", status_code=200)
    )

    with ValidationContext(disable_cache=True):
        reader = get_reader(url)
        assert len(route.calls) == 1
        reader = get_reader(url)  # second call to check cache
        assert len(route.calls) == 2

    assert reader.original_root == RootHttpUrl("https://mock_example.com/files")
    assert reader.original_file_name == "my_bioimageio.yaml"
    assert reader.read().decode(encoding="utf-8") == "example content"


def test_download_zip_wo_cache(respx_mock: MockRouter):
    from bioimageio.spec._internal.io import get_reader

    remote_data = io.BytesIO()
    content = {"bioimageio.yaml": "ref: my_file.txt", "my_file.txt": "example content"}
    with ZipFile(remote_data, mode="w") as remote_zip:
        for k, v in content.items():
            remote_zip.writestr(k, v)

    remote_content = remote_data.getvalue()
    url = "https://mock_example.com/files/my.zip"
    route = respx_mock.get(url).mock(
        httpx.Response(content=remote_content, status_code=200)
    )

    with ValidationContext(disable_cache=True):
        reader = get_reader(url)

    assert len(route.calls) == 1
    assert reader.original_file_name == "my.zip"

    # resolve subpath within downloaded zip
    with ZipFile(reader, mode="r") as zf:
        for k, v in content.items():
            assert k in zf.namelist()
            assert zf.read(k).decode(encoding="utf-8") == v

            # check alternative access
            subpath = ZipPath(zf, k)
            assert subpath.exists()
            assert subpath.read_text(encoding="utf-8") == v


def test_serialize_file_descr():
    from bioimageio.spec._internal.io import FileDescr

    path = Path(__file__).absolute()
    path_str = str(path)
    file_descr = FileDescr(source=path)

    data = file_descr.model_dump(mode="json")

    assert data["source"] == path_str


def test_serialize_absolute_file_path():
    from pydantic import FilePath, RootModel

    path = Path(__file__).absolute()
    path_str = str(path)
    file_path = RootModel[FilePath](path)

    data = file_path.model_dump(mode="json")

    assert data == path_str


def test_fail_relative_file_path_from_absolute():
    from bioimageio.spec._internal.io import RelativeFilePath

    path = Path(__file__).absolute()
    with pytest.raises(ValueError):
        _ = RelativeFilePath(path)


def test_relative_directory():
    from pydantic import RootModel

    from bioimageio.spec._internal.io import RelativeDirectory

    path = Path(__file__).parent.relative_to(Path().absolute())
    rel_dir = RelativeDirectory(path)

    assert (
        RootModel[RelativeDirectory](rel_dir).model_dump(mode="python")
        == path.as_posix()
    )
    assert (
        RootModel[RelativeDirectory](rel_dir).model_dump(mode="json") == path.as_posix()
    )

    with pytest.raises(ValueError):
        _ = RelativeDirectory(path.absolute())


def test_serialize_relative_file_path_from_left_to_right_union():
    from pydantic import FilePath, RootModel

    from bioimageio.spec._internal.io import RelativeFilePath

    path = Path(__file__).absolute()
    path_str = str(path)
    file_path = RootModel[
        Annotated[Union[RelativeFilePath, FilePath], Field(union_mode="left_to_right")]
    ](path)
    assert isinstance(file_path, RootModel)
    assert not isinstance(file_path.root, RelativeFilePath)

    data = file_path.model_dump(mode="json")

    assert data == path_str


def test_serialize_relative_file_path_from_union():
    from pydantic import FilePath, RootModel

    from bioimageio.spec._internal.io import RelativeFilePath

    path = Path(__file__).absolute()
    path_str = str(path)
    file_path = RootModel[Union[RelativeFilePath, FilePath]](path)

    data = file_path.model_dump(mode="json")

    assert data == path_str


def test_open_url_with_wrong_sha(respx_mock: MockRouter):
    from bioimageio.spec._internal.io import (
        _open_url,  # pyright: ignore[reportPrivateUsage]
    )

    url = "https://example.com/file.txt"
    sha = Sha256("0" * 64)  # invalid sha256 for testing

    _ = respx_mock.get(url).mock(side_effect=httpx.InvalidURL("Invalid URL"))

    with pytest.raises(httpx.InvalidURL, match="Invalid URL"):
        _ = _open_url(HttpUrl(url), sha256=sha, progressbar=False)
