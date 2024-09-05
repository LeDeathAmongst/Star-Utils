# Thanks to @Vexed01 on GitHub for this code (https://github.com/Vexed01/Vex-Cogs)!
# Copy the utils from https://github.com/AAA3A-AAA3A/AAA3A_utils to each cog in this repo.

import datetime
import json
import os
import shutil
from pathlib import Path
import ast
import astor

import git
from git import Repo

VERSION = 1.1
BASE_PATH = Path("/root")

# Function to modify Python files
def modify_python_file(file_path):
    with open(file_path, 'r') as file:
        source_code = file.read()

    # Parse the source code into an AST
    tree = ast.parse(source_code)

    class ModifyCog(ast.NodeTransformer):
        def visit_Attribute(self, node):
            if isinstance(node.value, ast.Name) and node.value.id == "commands" and node.attr == "Cog":
                return ast.Name(id="Cog", ctx=ast.Load())
            return node

    # Modify the AST
    modifier = ModifyCog()
    modified_tree = modifier.visit(tree)

    # Add import statement if not present
    import_found = any(
        isinstance(node, ast.ImportFrom) and node.module == "Star_Utils" and
        any(alias.name == "Cog" for alias in node.names) for node in modified_tree.body
    )
    if not import_found:
        import_node = ast.ImportFrom(module="Star_Utils", names=[ast.alias(name="Cog", asname=None)], level=0)
        modified_tree.body.insert(0, import_node)

    # Convert the modified AST back to source code
    modified_code = astor.to_source(modified_tree)

    # Write the modified code back to the file
    with open(file_path, 'w') as file:
        file.write(modified_code)

# Process the utils and cogs
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
    for path in (BASE_PATH / "StarCogs").iterdir()
    if (
        path.is_dir()
        and not path.name.startswith((".", "_"))
        and path.name != "docs"
    )
]
cog_folders = [cog.lower() for cog in all_cogs]
for cog in cog_folders:
    destination = (
        BASE_PATH / "StarCogs" / cog / "Star_Utils"
    )
    if destination.exists():
        shutil.rmtree(destination)
    if VERSION is None:
        shutil.copytree(utils_location, destination)
    else:
        destination = BASE_PATH / "StarCogs" / cog
        with open(destination / "utils_version.json", "w") as fp:
            fp.write(json.dumps({"needed_utils_version": VERSION}))

    # Modify Python files in the cog directory
    for py_file in destination.glob("*.py"):
        modify_python_file(py_file)

if VERSION is None:
    utils_repo.close()
    shutil.rmtree(utils_repo_clone_location)
