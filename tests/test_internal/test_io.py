import io
from pathlib import Path, PurePath
from typing import Any
from zipfile import ZipFile

import httpx
import pytest
from pydantic import ValidationError
from respx import MockRouter

from bioimageio.spec import ValidationContext
from bioimageio.spec._internal.io_basics import ZipPath
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

    with ValidationContext(disable_cache=False):
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
