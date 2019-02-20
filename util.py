import os
from pathlib import Path

from git import Git, Repo

HERE = Path(__file__).resolve().parent
ROOT = HERE
UPSTREAM = ROOT / "upstream"
UPSTREAM.mkdir(exist_ok=True)
UPSTREAM = ROOT / "upstream"
UPSTREAM.mkdir(exist_ok=True)
NO_RESET = "NO_RESET" in os.environ


def get_repo(name: str, url: str, branch: str = "master") -> Repo:
    try:
        repo = Repo(UPSTREAM / name)
    except Exception:
        Git(UPSTREAM).clone(url)
        repo = Repo(UPSTREAM / name)

    if NO_RESET is False:
        repo.head.reset(index=True, working_tree=True)
        raw_git = repo.git
        raw_git.clean("-xdf")
        repo.remote().pull(refspec=branch, rebase=True)
        assert not repo.is_dirty()

    return repo
