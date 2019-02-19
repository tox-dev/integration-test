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


def get_repo(name: str, url: str) -> Repo:
    try:
        repo = Repo(UPSTREAM / name)
        if NO_RESET is False:
            repo.remote("origin").pull(refspec="master")
            repo.head.reset(index=True, working_tree=True)
            raw_git = repo.git
            raw_git.clean("-xdf")
            assert not repo.is_dirty()
    except Exception:
        Git(UPSTREAM).clone(url)
        repo = Repo(UPSTREAM / name)

    return repo
