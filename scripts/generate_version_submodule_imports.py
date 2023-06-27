from difflib import ndiff
import re
import sys
from argparse import ArgumentParser
from dataclasses import dataclass, field
from pathlib import Path

import black.files
import black.mode

ROOT_PATH = Path(__file__).parent.parent

AUTOGEN_START = "# autogen: start\n"
AUTOGEN_BODY = """from . import {info.all_version_modules_plain}
from .{info.latest_version_module} import LATEST_FORMAT_VERSION, FormatVersion, {info.target_node}, LatestFormatVersion

__all__ = [{info.all_version_modules_quoted},
    "LATEST_FORMAT_VERSION",
    "FormatVersion",
    "{info.target_node}",
    "LatestFormatVersion"
]
"""
AUTOGEN_STOP = "\n# autogen: stop\n"

VERSION_MODULE_PATTERN = r"v(?P<major>\d+)_(?P<minor>\d+).py"


def main():
    args = parse_args()
    for target in ["generic", "model", "dataset", "collection"]:
        process(
            Info(target=target, all_version_modules=get_ordered_version_submodules(target)),
            check=args.command == "check",
        )

    return 0


def parse_args():
    p = ArgumentParser(description=("script that generates imports in bioimageio.spec resource description submodules"))
    p.add_argument("command", choices=["check", "generate"])
    args = p.parse_args()
    return args


@dataclass
class Info:
    target: str
    all_version_modules: list[str]
    target_node: str = field(init=False)
    latest_version_module: str = field(init=False)
    all_version_modules_quoted: str = field(init=False)
    all_version_modules_plain: str = field(init=False)
    package_path: Path = field(init=False)

    def __post_init__(self):
        self.target_node = dict(generic="GenericDescription").get(self.target, self.target.capitalize())
        self.latest_version_module = self.all_version_modules[-1]
        self.all_version_modules_quoted = ",\n".join(f'"{vm}"' for vm in self.all_version_modules)
        self.all_version_modules_plain = ", ".join(self.all_version_modules)
        self.package_path = (ROOT_PATH / "bioimageio" / "spec" / self.target).resolve()


def process(info: Info, check: bool):
    package_init = info.package_path / "__init__.py"
    print(f"{'Checking' if check else 'Updating'} {package_init}")

    init_content = package_init.read_text()
    pattern = AUTOGEN_START + ".*" + AUTOGEN_STOP
    flags = re.DOTALL
    if not re.findall(pattern, init_content, flags=flags):
        raise RuntimeError(
            f"Could not find autogen markers in {package_init}. Expected to find:\n{AUTOGEN_START}...{AUTOGEN_STOP}"
        )

    updated = re.sub(pattern, AUTOGEN_START + AUTOGEN_BODY.format(info=info) + AUTOGEN_STOP, init_content, flags=flags)
    black_config = black.files.parse_pyproject_toml(str(ROOT_PATH / "pyproject.toml"))
    black_config["target_versions"] = set(
        (getattr(black.mode.TargetVersion, tv.upper()) for tv in black_config.pop("target_version"))
    )
    updated = black.format_str(updated, mode=black.mode.Mode(**black_config))

    if check:
        if init_content == updated:
            print("all seems fine")
        else:
            raise RuntimeError(
                "call with mode 'generate' to update:\n"
                + "".join(ndiff(init_content.splitlines(keepends=True), updated.splitlines(keepends=True)))
            )
    else:
        package_init.write_text(updated)


def get_ordered_version_submodules(target: str):
    matches = [
        m
        for p in (ROOT_PATH / "bioimageio" / "spec" / target).iterdir()
        if p.is_file() and (m := re.fullmatch(VERSION_MODULE_PATTERN, p.name))
    ]
    if not matches:
        raise RuntimeError(f"No version modules found for target '{target}'")

    return [m.string[:-3] for m in sorted(matches, key=lambda m: (int(m["major"]), int(m["minor"])))]


if __name__ == "__main__":
    sys.exit(main())
