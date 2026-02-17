from pathlib import Path


def test_cache_path(tmp_path: Path):
    from bioimageio.spec._internal._settings import settings
    from bioimageio.spec.utils import empty_cache, get_reader

    original_cache_path = settings.cache_path
    try:
        settings.cache_path = tmp_path
        assert "disk_cache" not in settings.__dict__
        assert settings.cache_path == tmp_path
        _ = get_reader(
            "https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/refs/heads/main/README.md"
        ).read()
        assert "disk_cache" in settings.__dict__
        assert settings.disk_cache.dir_path == tmp_path
        assert len([fn for fn in tmp_path.iterdir() if fn.suffix != ".lock"]) == 1
        empty_cache()
        assert len([fn for fn in tmp_path.iterdir() if fn.suffix != ".lock"]) == 0
    finally:
        settings.cache_path = original_cache_path
