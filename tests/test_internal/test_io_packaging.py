from pathlib import Path
from typing import Dict


def test_package_file_descr():
    from bioimageio.spec._internal.io import FileDescr
    from bioimageio.spec._internal.io_basics import FileName
    from bioimageio.spec._internal.io_packaging import FileDescr_
    from bioimageio.spec._internal.node import Node
    from bioimageio.spec._internal.packaging_context import PackagingContext

    class MyNode(Node):
        important_file: FileDescr_

    my_obj = MyNode(important_file=FileDescr(source=Path(__file__)))
    my_obj_serialized = my_obj.model_dump(mode="json", exclude_none=True)
    assert my_obj_serialized["important_file"] == dict(source=str(Path(__file__)))

    file_sources: Dict[FileName, FileDescr] = {}
    with PackagingContext(
        bioimageio_yaml_file_name="bioimageio.yaml", file_sources=file_sources
    ):
        _ = my_obj.model_dump(mode="json")

    assert Path(__file__).name in file_sources
