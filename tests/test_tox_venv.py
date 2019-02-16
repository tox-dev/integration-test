import subprocess
import sys

import pytest
from util import get_repo


@pytest.fixture(scope="session")
def tox_venv_repo():
    # noinspection PyBroadException
    tox = get_repo(name="tox-venv", url="https://github.com/tox-dev/tox-venv.git")
    return tox


def test_venv_tox_call(tox_venv_repo):
    subprocess.check_call([sys.executable, "-m", "tox"], cwd=tox_venv_repo.working_tree_dir)
