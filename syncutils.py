# Thanks to @Vexed01 on GitHub for this code (https://github.com/Vexed01/Vex-Cogs)!
# Copy the utils from https://github.com/AAA3A-AAA3A/AAA3A_utils to each cog in this repo.

import datetime
import json
import os
import shutil
from pathlib import Path

import git
from git import Repo

# git -C %USERPROFILE%\Documents\GitHub\AAA3A_utils rev-list HEAD --count AAA3A_utils
VERSION = 6.8
BASE_PATH = Path(os.environ["USERPROFILE"]) / "Documents" / "GitHub"

if VERSION is None:
    utils_repo_clone_location = BASE_PATH / "Star_Utils_clone_for_sync"
    utils_repo = Repo.clone_from(
        "https://github.com/LeDeathAmongst/Star_Utils.git", utils_repo_clone_location
    )

    utils_location = utils_repo_clone_location / "Star_Utils"
    commit = utils_repo.head.commit

    README_MD_TEXT = """## My utils

    Hello there! If you're contributing or taking a look, everything in this folder
    is synced from a master repo at https://github.com/LeDeathAmongst/Star_Utils by GitHub Actions -
    so it's probably best to look/edit there.

    ---

    Last sync at: {time}
    Commit: [`{commit}`](https://github.com/LeDeathAmongst/Star_Utils/commit/{commit})
    """
    readme = README_MD_TEXT.format(
        time=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z"),
        commit=commit,
    )

    with open(utils_location / "README.md", "w") as fp:
        fp.write(readme)

    with open(utils_location / "commit.json", "w") as fp:
        fp.write(json.dumps({"latest_commit": str(commit)}))
else:
    with open(BASE_PATH / "Star_Utils" / "Star_Utils" / "__version__.py", "w") as fp:
        fp.write(f"__version__ = {VERSION}\n")

all_cogs = [
    path.name
    for path in (BASE_PATH / "Star-Cogs").iterdir()
    if (
        path.is_dir()
        and not path.name.startswith((".", "_"))
        and path.name != "docs"
    )
]
cog_folders = [cog.lower() for cog in all_cogs]
for cog in cog_folders:
    destination = (
        BASE_PATH / "Star-Cogs" / cog / "Star_Utils"
    )
    if destination.exists():
        shutil.rmtree(destination)
    if VERSION is None:
        shutil.copytree(utils_location, destination)
    else:
        destination = BASE_PATH / "Star-Cogs" / cog
        with open(destination / "utils_version.json", "w") as fp:
            fp.write(json.dumps({"needed_utils_version": VERSION}))

if VERSION is None:
    utils_repo.close()
    git.rmtree(utils_repo_clone_location)
