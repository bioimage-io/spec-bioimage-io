import json
import os
from copy import deepcopy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from types import SimpleNamespace
from typing import Any, Dict, List, Protocol
from unittest import SkipTest

import pytest


class MonkeyPatch(Protocol):
    def setattr(
        self, target: object, name: str, value: object, raising: bool = True
    ) -> None: ...


def test_upload_keeps_remote_files_as_references(monkeypatch: MonkeyPatch) -> None:
    import bioimageio.spec._upload as upload_module
    from bioimageio.spec._internal._settings import settings
    from bioimageio.spec._internal.io_basics import BIOIMAGEIO_YAML

    posts: List[Dict[str, Any]] = []
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
        posts.append({"url": url, "kwargs": deepcopy(kwargs)})
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
    assert posts[0]["kwargs"]["json"]["manifest"] == {
        "format_version": "0.5.0",
        "name": "Test Model",
        "type": "model",
    }
    assert posts[1]["kwargs"]["json"] == {
        "artifact_id": "test-artifact",
        "file_path": BIOIMAGEIO_YAML,
    }
    assert posts[2]["kwargs"]["json"]["manifest"]["status"] == "request-review"


def test_upload_with_local_http_traffic(monkeypatch: MonkeyPatch) -> None:
    import bioimageio.spec._upload as upload_module
    from bioimageio.spec._internal._settings import settings
    from bioimageio.spec._internal.io_basics import BIOIMAGEIO_YAML

    requests: List[Dict[str, Any]] = []
    base_url = ""
    descr = SimpleNamespace(id=None, name="Test Model", type="model", version=None)

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

    class UploadHandler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: object) -> None:
            pass

        def _read_body(self) -> bytes:
            return self.rfile.read(int(self.headers.get("Content-Length", "0")))

        def _record(self, method: str) -> bytes:
            body = self._read_body()
            content_type = self.headers.get("Content-Type", "")
            requests.append(
                {
                    "method": method,
                    "path": self.path,
                    "headers": dict(self.headers),
                    "body": body,
                    "json": (
                        json.loads(body)
                        if body and content_type == "application/json"
                        else None
                    ),
                }
            )
            return body

        def _write_json(self, payload: object) -> None:
            body = json.dumps(payload).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            _ = self.wfile.write(body)

        def do_POST(self) -> None:
            _ = self._record("POST")
            if self.path == "/create":
                self._write_json({"id": "test-artifact"})
            elif self.path == "/put_file":
                self._write_json(f"{base_url}/upload")
            elif self.path == "/edit":
                self._write_json({})
            else:
                self.send_error(404)

        def do_PUT(self) -> None:
            _ = self._record("PUT")
            if self.path == "/upload":
                self._write_json({})
            else:
                self.send_error(404)

    monkeypatch.setattr(settings, "hypha_upload_token", "test-token")
    server = ThreadingHTTPServer(("127.0.0.1", 0), UploadHandler)
    base_url = f"http://127.0.0.1:{server.server_port}"
    monkeypatch.setattr(upload_module, "load_description", load_description)
    monkeypatch.setattr(upload_module, "get_package_content", get_package_content)
    monkeypatch.setattr(settings, "hypha_upload", f"{base_url}/create")

    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        url = upload_module.upload("source.yaml", keep_remote_files_as_references=True)
    finally:
        server.shutdown()
        thread.join()
        server.server_close()

    assert str(url) == (
        "https://hypha.aicell.io/bioimage-io/artifacts/test-artifact/files/"
        + "rdf.yaml?version=stage"
    )
    assert requests[0]["path"] == "/create"
    assert requests[0]["json"]["manifest"] == {
        "format_version": "0.5.0",
        "name": "Test Model",
        "type": "model",
    }
    assert requests[1]["path"] == "/put_file"
    assert requests[1]["json"] == {
        "artifact_id": "test-artifact",
        "file_path": BIOIMAGEIO_YAML,
    }
    assert requests[2]["path"] == "/upload"
    assert b"name: Test Model" in requests[2]["body"]
    assert requests[3]["path"] == "/edit"
    assert requests[3]["json"]["manifest"]["status"] == "request-review"


@pytest.mark.skipif(
    os.getenv("RUN_REAL_UPLOAD_TESTS") != "true",
    reason="enable by RUN_REAL_UPLOAD_TESTS='true'",
)
def test_upload_with_settings_hypha_upload_endpoint(unet2d_path: Path) -> None:
    from bioimageio.spec._internal._settings import settings
    from bioimageio.spec._upload import upload

    if settings.hypha_upload_token is None:
        raise SkipTest("BIOIMAGEIO_HYPHA_UPLOAD_TOKEN is not set")

    url = upload(unet2d_path, keep_remote_files_as_references=True)

    assert str(url).startswith("https://hypha.aicell.io/bioimage-io/artifacts/")
    assert str(url).endswith("/files/rdf.yaml?version=stage")
