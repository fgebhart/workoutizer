from pathlib import Path

import tomli


def _get_version_from_project_toml():
    with open(Path(__file__).parent.parent / "pyproject.toml", "rb") as f:
        toml_dict = tomli.load(f)

    return toml_dict["tool"]["poetry"]["version"]


__version__ = _get_version_from_project_toml()
