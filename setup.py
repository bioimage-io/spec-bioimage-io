import json
from pathlib import Path

from setuptools import find_namespace_packages, setup

# Get the long description from the README file
ROOT_DIR = Path(__file__).parent.resolve()
long_description = (ROOT_DIR / "README.md").read_text(encoding="utf-8")
VERSION_FILE = ROOT_DIR / "bioimageio" / "spec" / "VERSION"
VERSION = json.loads(VERSION_FILE.read_text(encoding="utf-8"))["version"]

_ = setup(
    name="bioimageio.spec",
    version=VERSION,
    description="Parser and validator library for bioimage.io specifications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bioimage-io/spec-bioimage-io",
    author="bioimage.io Team",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    packages=find_namespace_packages(exclude=["tests"]),  # Required
    install_requires=[
        "annotated-types>=0.5.0,<1",
        "email_validator",
        "imageio",
        "loguru",
        "markdown",
        "numpy>=1.21",
        "packaging>=17.0",
        "pooch>=1.5,<2",
        "pydantic-settings>=2.5,<3",
        "pydantic>=2.7.0,<2.10",  # TODO: check and update pin after https://github.com/pydantic/pydantic/pull/11008 is released
        "python-dateutil",
        "requests",
        "rich",
        "ruyaml",
        "tifffile>=2020.7.4",
        "tqdm",
        "typing-extensions",
        "zipp",
    ],
    extras_require={
        "tests": (
            test_extras := [
                "deepdiff",
                "jsonschema",
                "lxml",
                "pytest-cov",
                "pytest",
                "requests-mock",
            ]
        ),
        "dev": (
            test_extras
            + [
                "black",
                # "json_schema_for_humans; python_version < 3.13",
                "jupyter-black",
                "jupyter",
                "pdoc",
                "pre-commit",
                "pyright==1.1.398",
                "ruff",
            ]
        ),
    },
    scripts=[],
    include_package_data=True,
    project_urls={
        "Bug Reports": "https://github.com/bioimage-io/spec-bioimage-io/issues",
        "Source": "https://github.com/bioimage-io/spec-bioimage-io",
    },
)
