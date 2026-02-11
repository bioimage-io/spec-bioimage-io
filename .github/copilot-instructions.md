# BioImage.IO Multi-Repo Workspace - AI Coding Agent Instructions

## Architecture Overview

This is a **multi-repo workspace** containing four interdependent projects for the BioImage.IO ecosystem:

1. **spec-bioimage-io**: Core specification parser and validator (Pydantic-based)
2. **core-bioimage-io-python**: Python implementation for running ML models from specs
3. **stardist**: Partner library for star-convex object detection
4. **genericache**: Shared caching library used by spec and core

### Key Relationships
- `core` depends on `spec` (pinned in pyproject.toml: `bioimageio.spec ==0.5.6.0`)
- Both use `genericache` for file caching
- `stardist` integrates via `bioimageio_utils.py` for BioImage.IO model export

## Critical Patterns

### YAML 1.2 Over PyYAML
**Always use `ruyaml` for YAML operations, NOT PyYAML.**
- Import: `from ruyaml import YAML` or use `bioimageio.spec._internal.io_utils.read_yaml`
- BioImage.IO specs are in YAML 1.2; PyYAML only supports YAML 1.1
- Entry files: `rdf.yaml` or `bioimageio.yaml`

### Pydantic Schema Architecture (spec-bioimage-io)
All resource descriptions inherit from `Node` (wraps `pydantic.BaseModel`):
- **Descr classes**: `ModelDescr`, `DatasetDescr`, etc. represent versioned specs (v0_4, v0_5)
- **ValidationContext**: Thread-safe context manager controlling validation behavior
  - `perform_io_checks`: Toggle expensive file downloads/verification
  - `known_files`: Bypass file downloads during testing (currently also used when checking uploads on bioimage.io when bioimageio.spec is run on a Hypha server while pending uploads are not yet uploaded.)
  - Access via `get_validation_context()` (contextvars)
- **Discriminated unions**: Use `type` field to distinguish resource types
- Example: [v0_5.py](src/bioimageio/spec/model/v0_5.py) defines `ModelDescr`, axes, preprocessing operations

### Validation & Error Handling
- Use `ValidationSummary` for structured validation results with error/warning levels
- `InvalidDescr`: Special Pydantic model for gracefully handling malformed descriptions
- Warning levels: `INFO`, `ALERT`, `ERROR` (see `_internal/warning_levels.py`)
- Test validation with: `bioimageio.spec.build_description(source, context=ValidationContext(...))`

### File Operations
- `FileDescr`: Pydantic node for local/remote file references with SHA256 verification
- Cache downloads in `bioimageio_cache/` (configurable via `BIOIMAGEIO_CACHE_PATH`)
- Use `BioimageioYamlContent` to represent parsed RDF files with their root context

## Development Workflows

### Running Tests
```bash
# spec-bioimage-io
pytest -v --cov bioimageio  # Basic tests
pytest -v --capture no  # See print statements
RUN_EXPENSIVE_TESTS=true pytest  # Include slow integration tests

# core-bioimage-io-python
pytest --disable-pytest-warnings  # Often needed due to TF/torch warnings
pytest tests/test_bioimageio_collection.py::test_rdf_format_to_populate_cache  # Populate cache

# stardist
pytest -v --durations=50  # Show slowest tests
```

### Code Quality (Both spec & core)
```bash
ruff check  # Linting (replaces flake8, isort, etc.)
ruff format  # Formatting (replaces black)
pyright -p pyproject.toml --pythonversion 3.9  # Type checking (pinned to 1.1.407)
```

### CLI Tools
```bash
# spec: Validate any BioImage.IO resource
bioimageio validate <path-or-url-to-rdf.yaml>

# core: Test model end-to-end (preprocessing, inference, postprocessing)
bioimageio test powerful-chipmunk  # Test by model nickname
bioimageio test path/to/rdf.yaml   # Test local model
```

### Package Structure Convention
Both spec and core use namespace packages under `bioimageio/`:
- Source in `src/bioimageio/{spec,core}/`
- Version: `__version__` in `__init__.py` (core) or `_version.py` (spec)
- Dynamic versioning in pyproject.toml: `version = { attr = "bioimageio.core.__version__" }`

## Project-Specific Notes

### spec-bioimage-io
- **Auto-generated imports**: Run `python scripts/generate_version_submodule_imports.py check` before committing
- **Format versions**: Each resource type has multiple versions (e.g., `v0_4.py`, `v0_5.py`)
  - Latest = type alias to newest version
  - `AnyModelDescr` = union of all model versions
- **Testing expensive ops**: Set `RUN_EXPENSIVE_TESTS=true` to test full model zoo validation

### core-bioimage-io-python
- **Prediction pipeline**: `create_prediction_pipeline()` → `PredictionPipeline` (encapsulates model + weights)
- **Sample**: Core data structure (`Sample` class) for tensors + metadata
- **Backends**: Pluggable weight format support in `backends/` (pytorch, tensorflow, onnx)
- **Partners**: Optional integrations (`stardist`, `careamics`) in `[partners]` extras

### stardist
- **Config classes**: `Config2D`/`Config3D` store training hyperparameters
- **BioImage.IO export**: Use `bioimageio_utils.py` functions, NOT manual YAML creation
- **Pre-trained models**: Accessed via `StarDist2D.from_pretrained('2D_versatile_fluo')`

### genericache
- **Type-safe caching**: `DiskCache[str].create(url_type=str, ...)`
- **Digest types**: `UrlDigest.from_str()` for URL-based cache keys
- **Multi-process safe**: Uses file locking for concurrent access

## Common Pitfalls

1. **Don't use PyYAML**: Will fail on YAML 1.2 features (boolean parsing, etc.)
2. **Context matters**: Always provide `ValidationContext` when building descriptions in tests
3. **Namespace packages**: Don't add `__init__.py` in `src/` (breaks namespace package)
4. **Cache pollution**: Set `BIOIMAGEIO_CACHE_PATH` to temp dir for isolated test runs
5. **Version mismatches**: When editing spec, remember to update core's pinned dependency

## Documentation Links

- Spec docs: https://bioimage-io.github.io/spec-bioimage-io
- Core docs: https://bioimage-io.github.io/core-bioimage-io-python
- Model zoo: https://bioimage.io
- CI builds test against multiple Python (3.9-3.13) and Pydantic versions (2.11+)
