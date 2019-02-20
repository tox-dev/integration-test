import os
import shutil
import socket
import subprocess
import sys
from contextlib import closing, contextmanager
from pathlib import Path

import pytest
import semver

from util import get_repo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

WHEELS = ROOT / "wheels"
WHEELS.mkdir(exist_ok=True)


@pytest.fixture(scope="session")
def git_tox():
    # noinspection PyBroadException
    tox = get_repo(
        name="tox", url="https://github.com/tox-dev/tox.git", branch=os.environ.get("TEST_AGAINST_BRANCH", "master")
    )
    return tox


@pytest.fixture(scope="session")
def tox_wheel(git_tox):
    try:
        max_version = None
        for tags in git_tox.tags:
            try:
                version = semver.parse_version_info(tags.name)
                if max_version is None:
                    max_version = version
                else:
                    max_version = max(version, max_version)
            except ValueError:
                continue
        assert max_version is not None
        new_version = semver.bump_minor(str(max_version))
        git_tox.create_tag(new_version)
        try:
            wheel = build_wheel(git_tox.working_tree_dir, "tox")
        finally:
            git_tox.delete_tag(new_version)
    finally:
        pass
    return wheel


def build_wheel(folder: Path, name: str):
    wheel_at = WHEELS / name
    shutil.rmtree(wheel_at)
    wheel_at.mkdir()
    subprocess.check_call(
        [sys.executable, "-m", "pip", "wheel", "--no-deps", "-w", str(wheel_at), "."], cwd=str(folder)
    )
    output = list(wheel_at.iterdir())
    assert len(output) == 1
    return output[0]


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def devpi(tox_wheel):
    devpi_path = ROOT / "devpi"
    if devpi_path.exists():
        shutil.rmtree(devpi_path)
    devpi_path.mkdir(exist_ok=True)

    with with_server(devpi_path) as url:
        devpi = Path(sys.executable).parent / "devpi"
        devpi_client_at = devpi_path / "client"
        devpi_client_at.mkdir(exist_ok=True)
        generic_args = ["--clientdir", ".", "-v", "-v"]

        user_name = "lancelot"
        password = "whatever"
        index = "dev"
        commands = [
            [devpi, "use"] + generic_args + [url],
            [devpi, "user"] + generic_args + ["-c", user_name, f"password={password}"],
            [devpi, "login"] + generic_args + [user_name, f"--password={password}"],
            [devpi, "index"] + generic_args + ["-c", index, "bases=root/pypi"],
            [devpi, "index"] + generic_args + ["-l"],
            [devpi, "use"] + generic_args + [f"{user_name}/{index}"],
        ]
        for wheel in (tox_wheel,):
            commands.append([devpi] + generic_args + ["upload", wheel])
        for command in commands:
            print(f'{devpi_client_at}$ {" ".join(str(i) for i in command)}')
            subprocess.check_call(command, cwd=devpi_client_at, universal_newlines=True)
        yield f"{url}/{user_name}/{index}"


@contextmanager
def with_server(devpi_path):
    devpi_server_at = devpi_path / "server"
    devpi_server_at.mkdir(exist_ok=True)

    port = find_free_port()
    devpi_server = Path(sys.executable).parent / "devpi-server"

    general = ["--serverdir", str(devpi_server_at), "--port", str(port)]

    subprocess.check_call([devpi_server, "--start", "--init"] + general, cwd=devpi_server_at, universal_newlines=True)
    try:
        yield f"http://localhost:{port}"
    finally:
        subprocess.check_call([devpi_server, "--stop"] + general, cwd=devpi_server_at, universal_newlines=True)
