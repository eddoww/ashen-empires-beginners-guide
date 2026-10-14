# Repository workflow

After completing requested changes, run the appropriate checks, commit all changes made for the task, and
push the current branch to its configured upstream automatically. The user has authorized this workflow for
every change; do not ask for confirmation before routine commits and pushes.

For guide content changes, edit `guide.md` and rebuild the site with `python3 tools/build.py` before committing.
Include the generated changes under `docs/` in the commit.

When adding gameplay tips, research the relevant sources and make the advice actionable. For quests, verify
the names, prerequisites, NPCs, objectives, locations and rewards, recommend a useful order, and explain the
steps a player must follow. Link the supporting sources and distinguish player recommendations from verified
quest details. Resolve misleading item names and source disagreements before publishing.
