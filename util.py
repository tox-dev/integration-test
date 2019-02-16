from pathlib import Path

from git import Repo, Git

HERE = Path(__file__).resolve().parent
ROOT = HERE
UPSTREAM = ROOT / "upstream"
UPSTREAM.mkdir(exist_ok=True)
UPSTREAM = ROOT / "upstream"
UPSTREAM.mkdir(exist_ok=True)


def get_repo(name: str, url: str) -> Repo:
    try:
        repo = Repo(UPSTREAM / name)
        repo.remote("origin").pull(refspec="master")
        repo.head.reset(index=True, working_tree=True)
        raw_git = repo.git
        raw_git.clean("-xdf")
    except Exception as _:
        Git(UPSTREAM).clone(url)
        repo = Repo(UPSTREAM / name)
    assert not repo.is_dirty()
    return repo
