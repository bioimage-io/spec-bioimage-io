import warnings
from typing import Any, List, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator


class PipDeps(BaseModel):
    """Pip dependencies to include in conda dependecies"""

    pip: List[str] = Field(default_factory=list)

    def __lt__(self, other: Any):
        if isinstance(other, PipDeps):
            return len(self.pip) < len(other.pip)
        else:
            return False

    def __gt__(self, other: Any):
        if isinstance(other, PipDeps):
            return len(self.pip) > len(other.pip)
        else:
            return False


class CondaEnv(BaseModel):
    """Represenation of the content of a conda environment.yaml file"""

    name: Optional[str] = None
    channels: List[str] = Field(default_factory=list)
    dependencies: List[Union[str, PipDeps]] = Field(default_factory=list)

    @field_validator("name", mode="after")
    def _ensure_valid_conda_env_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        for illegal in ("/", " ", ":", "#"):
            value = value.replace(illegal, "")

        return value or "empty"

    @property
    def wo_name(self):
        return self.model_construct(**{k: v for k, v in self if k != "name"})

    def _get_version(self, package: str):
        """Helper to return any verison pin for **package**

        TODO: improve: interprete version pin and return structured information.
        """
        for d in self.dependencies:
            if isinstance(d, PipDeps):
                for p in d.pip:
                    if p.startswith(package):
                        return p[len(package) :]
            elif d.startswith(package):
                return d[len(package) :]


class BioimageioCondaEnv(CondaEnv):
    """A special `CondaEnv` that
    - automatically adds bioimageio specific dependencies
    - sorts dependencies
    """

    @model_validator(mode="after")
    def _normalize_bioimageio_conda_env(self):
        """update a conda env such that we have bioimageio.core and sorted dependencies"""
        for req_channel in ("conda-forge", "nodefaults"):
            if req_channel not in self.channels:
                self.channels.append(req_channel)

        if "defaults" in self.channels:
            warnings.warn("removing 'defaults' from conda-channels")
            self.channels.remove("defaults")

        if "pip" not in self.dependencies:
            self.dependencies.append("pip")

        for dep in self.dependencies:
            if isinstance(dep, PipDeps):
                pip_section = dep
                pip_section.pip.sort()
                break
        else:
            pip_section = None

        if (
            pip_section is not None
            and any(pd.startswith("bioimageio.core") for pd in pip_section.pip)
        ) and not any(
            d.startswith("bioimageio.core")
            or d.startswith("conda-forge::bioimageio.core")
            for d in self.dependencies
            if not isinstance(d, PipDeps)
        ):
            self.dependencies.append("conda-forge::bioimageio.core")

        self.dependencies.sort()
        return self
