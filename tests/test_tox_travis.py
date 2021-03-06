import os
import subprocess
import sys

import pytest

from util import get_repo


@pytest.fixture(scope="session")
def repo():
    # noinspection PyBroadException
    return get_repo(name="tox-travis", url="https://github.com/tox-dev/tox-travis.git")


def test_travis(repo, devpi):
    env = os.environ.copy()
    env["PIP_INDEX_URL"] = devpi
    subprocess.check_call([sys.executable, "-m", "tox", "-vv", "-r", "-e", "py39"], cwd=repo.working_tree_dir, env=env)
