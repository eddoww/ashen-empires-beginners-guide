# Repository workflow

After completing requested changes, run the appropriate checks, commit all changes made for the task, and
push the current branch to its configured upstream automatically. The user has authorized this workflow for
every change; do not ask for confirmation before routine commits and pushes.

For guide content changes, edit `guide.md` and rebuild the site with `python3 tools/build.py` before committing.
Include the generated changes under `docs/` in the commit.
