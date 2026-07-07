from copy import deepcopy
from types import SimpleNamespace
from typing import Any, Dict, List, Protocol, Tuple


class MonkeyPatch(Protocol):
    def setattr(
        self, target: object, name: str, value: object, raising: bool = True
    ) -> None: ...


def test_upload_keeps_remote_files_as_references(monkeypatch: MonkeyPatch) -> None:
    import bioimageio.spec._upload as upload_module
    from bioimageio.spec._internal._settings import settings
    from bioimageio.spec._internal.io_basics import BIOIMAGEIO_YAML

    posts: List[Tuple[str, Dict[str, Any]]] = []
    descr = SimpleNamespace(id=None, name="Test Model", type="model", version=None)

    class Response:
        payload: Any

        def __init__(self, payload: Any) -> None:
            super().__init__()
            self.payload = payload

        def json(self) -> Any:
            return self.payload

        def raise_for_status(self) -> "Response":
            return self

    def load_description(source: object) -> SimpleNamespace:
        assert source == "source.yaml"
        return descr

    def get_package_content(
        given_descr: object, *, local_files_only: bool
    ) -> Dict[str, Any]:
        assert given_descr is descr
        assert local_files_only is True
        return {
            BIOIMAGEIO_YAML: {
                "format_version": "0.5.0",
                "name": "Test Model",
                "type": "model",
            }
        }

    def post(url: str, **kwargs: Any) -> Response:
        posts.append((url, deepcopy(kwargs)))
        if url == settings.hypha_upload:
            return Response({"id": "test-artifact"})
        if url.endswith("/put_file"):
            return Response("https://example.com/upload")
        if url.endswith("/edit"):
            return Response({})

        raise AssertionError(url)

    def put(url: str, **kwargs: Any) -> Response:
        assert url == "https://example.com/upload"
        assert b"name: Test Model" in kwargs["files"][BIOIMAGEIO_YAML].read()
        assert kwargs["headers"] == {"Content-Type": ""}
        return Response({})

    monkeypatch.setattr(settings, "hypha_upload_token", "test-token")
    monkeypatch.setattr(upload_module, "load_description", load_description)
    monkeypatch.setattr(upload_module, "get_package_content", get_package_content)
    monkeypatch.setattr(upload_module.httpx, "post", post)
    monkeypatch.setattr(upload_module.httpx, "put", put)

    url = upload_module.upload("source.yaml", keep_remote_files_as_references=True)

    assert str(url) == (
        "https://hypha.aicell.io/bioimage-io/artifacts/test-artifact/files/"
        "rdf.yaml?version=stage"
    )
    assert posts[0][1]["json"]["manifest"] == {
        "format_version": "0.5.0",
        "name": "Test Model",
        "type": "model",
    }
    assert posts[1][1]["json"] == {
        "artifact_id": "test-artifact",
        "file_path": BIOIMAGEIO_YAML,
    }
    assert posts[2][1]["json"]["manifest"]["status"] == "request-review"
