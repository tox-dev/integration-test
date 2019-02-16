import shutil
import socket
import subprocess
import sys
from contextlib import closing
from pathlib import Path

import pytest

from util import get_repo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

WHEELS = ROOT / "wheels"
WHEELS.mkdir(exist_ok=True)

DEVPI = ROOT / "devpi"


@pytest.fixture(scope="session")
def git_tox():
    # noinspection PyBroadException
    tox = get_repo(name="tox", url="https://github.com/tox-dev/tox.git")
    return tox


@pytest.fixture(scope="session")
def tox_wheel(git_tox):
    wheel = build_wheel(git_tox.working_tree_dir, "tox")
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
    if DEVPI.exists():
        shutil.rmtree(DEVPI)
    DEVPI.mkdir(exist_ok=True)
    port = find_free_port()

    devpi_cmd = Path(sys.executable) / "devpi-server"
    devpi = Path(sys.executable) / "devpi"

    subprocess.check_call([devpi_cmd, "--start", "--init", "--serverdir", str(DEVPI), "--port", str(port)], cwd=DEVPI)
    try:
        yield
    finally:
        subprocess.check_call([devpi_cmd, "--stop", "--serverdir", str(DEVPI), "--port", str(port)], cwd=DEVPI)
