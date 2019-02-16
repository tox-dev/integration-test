import subprocess
import sys

import pytest
from util import get_repo


@pytest.fixture(scope="session")
def repo():
    # noinspection PyBroadException
    return get_repo(name="tox-pipenv", url="https://github.com/tox-dev/tox-pipenv.git")


def test_pipenv_tox_call(repo):
    subprocess.check_call([sys.executable, "-m", "tox", "-vv", "-e", "py37"], cwd=repo.working_tree_dir)
