import os
import shutil
import subprocess
import sys
from pathlib import Path

import luddite
import pytest
from packaging import version
from pytest_venv import VirtualEnvironment

from workoutizer import settings as django_settings
from workoutizer.settings import BASE_DIR

workoutizer = "workoutizer"


def _add_wkz_bin(venv: VirtualEnvironment) -> VirtualEnvironment:
    wkz = Path(venv.bin) / "wkz"
    setattr(venv, "wkz", wkz)
    return venv


@pytest.fixture(scope="function")
def build_wheel() -> Path:
    from workoutizer import __version__ as current_version

    # build wheel
    subprocess.check_output([sys.executable, "setup.py", "bdist_wheel"])
    # get path and yield it
    path_to_wheel = Path(django_settings.WORKOUTIZER_DIR) / "dist" / f"workoutizer-{current_version}-py3-none-any.whl"
    yield path_to_wheel


@pytest.fixture(scope="function")
def venv_with_latest_pypi_wkz(venv: VirtualEnvironment) -> VirtualEnvironment:
    """Fixture to install latest workoutizer from PyPi"""
    os.environ["WKZ_ENV"] = "devel"
    venv.install(workoutizer, upgrade=True)
    venv = _add_wkz_bin(venv)
    yield venv


@pytest.fixture(scope="function")
def venv_with_current_wkz(venv: VirtualEnvironment, build_wheel) -> VirtualEnvironment:
    """Fixture to install current local development version of workoutizer"""
    venv.install(str(build_wheel))
    # add wkz path as attribute to venv
    venv = _add_wkz_bin(venv)
    yield venv


def _replace_string_in_file(path: Path, orig: str, new: str) -> None:
    with open(path, "r") as f:
        filedata = f.read()
    filedata = filedata.replace(orig, new)
    with open(path, "w") as f:
        f.write(filedata)


def _mock_version(venv: VirtualEnvironment, version: str) -> None:
    # get path to installed init module to mock version
    init_path = Path(venv.path) / "lib" / f"python{sys.version[:3]}" / "site-packages" / "workoutizer" / "__init__.py"
    print(f"mocking version in file: {init_path}")
    _replace_string_in_file(init_path, 'pkg_resources.require("workoutizer")[0].version', f"'{version}'")


def test_upgrade_current_to_latest_pypi_version(venv_with_current_wkz):
    from workoutizer import __version__ as current_version

    wkz = venv_with_current_wkz.wkz
    print(f"venv path: {wkz}")
    subprocess.check_output([wkz, "init"])
    installed_version = subprocess.check_output([wkz, "-v"]).decode("utf-8").replace("\n", "")

    # check that the installed version equals the current version
    assert current_version == installed_version

    pypi_version = luddite.get_version_pypi("workoutizer")

    # upgrading now will not find a newer version, since current local
    # dev version is always larger than the latest version on pypi
    upgrading = subprocess.check_output([wkz, "upgrade"]).decode("utf-8")
    assert (
        f"Your installed version ({current_version}) seems to be greater than "
        f"the latest version on pypi ({pypi_version}).\n"
    ) == upgrading

    # mock version to be lower than the latest version on pypi
    dummy_version = "0.0.1"
    _mock_version(venv_with_current_wkz, dummy_version)
    mocked_version = subprocess.check_output([wkz, "-v"]).decode("utf-8").replace("\n", "")
    assert mocked_version == dummy_version

    # upgrading now will install the latest version from pypi
    upgrading = subprocess.check_output([wkz, "upgrade"]).decode("utf-8")
    assert (
        f"Newer version available: {pypi_version}. You are running: {dummy_version}\n" f"upgrading workoutizer..."
    ) in upgrading

    assert f"Successfully installed workoutizer-{pypi_version}" in upgrading
    assert "static files copied to" in upgrading
    assert "Running migrations:" in upgrading
    assert "System check identified no issues (0 silenced)." in upgrading
    assert f"Successfully upgraded from {dummy_version} to {pypi_version}" in upgrading

    # check that the installed version now equals the latest version on pypi
    installed_version = subprocess.check_output([wkz, "-v"]).decode("utf-8").replace("\n", "")
    assert pypi_version == installed_version


def test_upgrade_latest_pypi_to_current_version(venv_with_latest_pypi_wkz, build_wheel):
    from workoutizer import __version__ as current_version

    wkz = venv_with_latest_pypi_wkz.wkz
    print(f"venv path: {wkz}")

    subprocess.check_output([wkz, "init", "--demo"])
    installed_version = subprocess.check_output([wkz, "-v"]).decode("utf-8").replace("\n", "")
    pypi_version = luddite.get_version_pypi("workoutizer")
    assert pypi_version == installed_version

    # check that the current version is always greater than the installed latest version from pypi
    assert version.parse(current_version) > version.parse(installed_version)

    # upgrading now will not find a newer version, since installed
    # version equals the latest version on pypi
    upgrading = subprocess.check_output([wkz, "upgrade"]).decode("utf-8")
    assert f"No update available. You are running the latest version: {pypi_version}\n" == upgrading

    # get path to installed cli module to mock package installation
    cli_path = (
        Path(venv_with_latest_pypi_wkz.path)
        / "lib"
        / f"python{sys.version[:3]}"
        / "site-packages"
        / "workoutizer"
        / "cli.py"
    )

    # TODO remove following four lines once this code is released to pypi
    # it was required to ensure the latest implementation of the cli module is used for upgrading, i.e. in order to be
    # able to mock the correct lines
    # overwrite cli module from pypi with recent cli module
    shutil.copy(Path(BASE_DIR) / "workoutizer" / "cli.py", cli_path)

    # mock package in pip_install function to install the local dev wheel
    _replace_string_in_file(cli_path, 'package = f"{package}=={pypi_version}"', f"package = '{build_wheel}'")
    _replace_string_in_file(
        cli_path, 'pypi_version = luddite.get_version_pypi("workoutizer")', f"pypi_version = '{current_version}'"
    )

    # also mock version to pass the version check in order to allow subsequent upgrading
    dummy_version = "0.0.2"
    _mock_version(venv_with_latest_pypi_wkz, dummy_version)

    # upgrading now will install the latest version from pypi
    upgrading = subprocess.check_output([wkz, "upgrade"]).decode("utf-8")

    assert f"Successfully installed workoutizer-{current_version}" in upgrading
    assert "static files copied to" in upgrading
    assert "Running migrations:" in upgrading
    assert "System check identified no issues (0 silenced)." in upgrading
    assert f"Successfully upgraded from {dummy_version} to {current_version}" in upgrading

    # check that the installed version now equals the latest version on pypi
    installed_version = subprocess.check_output([wkz, "-v"]).decode("utf-8").replace("\n", "")
    assert current_version == installed_version
