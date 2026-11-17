# Working on the beginner's guide

This repo is a guide to the MMO Ashen Empires, published with GitHub Pages at
https://eddoww.github.io/ashen-empires-beginners-guide/. Pages publishes `docs/` from `main` about 30 seconds
after a push. There is no CI and no other branch.

## Repository workflow

After completing requested changes, run the appropriate checks, commit all changes made for the task, and
push the current branch to its configured upstream automatically. The user has authorized this workflow for
every change; do not ask for confirmation before routine commits and pushes.

For guide content changes, edit `guide.md` and rebuild the site with `python3 tools/build.py` before committing.
Include the generated changes under `docs/` in the commit.

## How it fits together

- `guide.md` is the whole guide as one text, and the only file to write in. Never edit `docs/*.html` or
  `docs/quests.js` by hand: `tools/build.py` regenerates them.
- `tools/build.py` cuts `guide.md` into pages at its `## ` headings. `PAGES` near the top of the script says which
  heading goes on which page and in what order. A `## ` heading that no page claims stops the build.
- `docs/app.js` and `docs/style.css` are written by hand. When you add a page, add it in three places: an entry
  in `PAGES`, its short name in the `names` map at the top of `docs/app.js`, and a row in the "If you want to
  know | Read" table at the top of `guide.md`.
- A Markdown table whose first column is headed `Quest` is special. Each row gets an anchor, a search entry,
  the quest's walkthrough links and its pictures, looked up by name in `images/manifest.json`. A column headed
  `Level` goes into the search too. Head other tables differently, or every row ends up in the search as a quest.
- A `::: pictures` block becomes a row of pictures; the README shows the format.

## Build and check

```sh
python3 tools/build.py            # needs the Python package "markdown"
```

The script prints the number of pages, quest rows and pictures. Before you commit, check that no internal link
points at an anchor that does not exist:

```sh
cd docs && python3 -c "
import re,glob
ids={f:set(re.findall(r'id=\"([^\"]+)\"',open(f).read())) for f in glob.glob('*.html')}
bad=[(f,h) for f in ids for h in re.findall(r'href=\"([^\"#:]*\.html)?#([^\"]+)\"',open(f).read()) if h[1] not in ids.get(h[0] or f,set())]
print('broken anchors:',bad)"
```

Anchors are the heading text in lower case, with runs of other characters turned into `-`. Leave apostrophes
out of headings you mean to link to.

To look at the site locally, run `python3 -m http.server 8000 -d docs` and open http://localhost:8000/.

## Pictures

Pictures come from AE Guides and the wiki. When a quest or a picture block is added:

```sh
python3 tools/collect_images.py <AE Guides pages> <wiki pages> data/wiki_pages.json
python3 tools/fetch_images.py     # needs ImageMagick; downloads and shrinks into docs/img
python3 tools/build.py
```

The two source folders already exist locally in `../ae-sources-archive/`: `aeguides/repo/` and `wiki/pages/`
(`<Title>.wiki`). Quests with no entry in the manifest still work; their row simply has no links or pictures. To
link such a quest anyway, write its name as a Markdown link to its wiki page.

## Sources

`../ae-sources-archive/` (outside this repo) is a local copy of every source the guide was written from: the
wiki's 384 articles and patch notes, AE Guides, AE Database with its bestiary, the Dragoneers' site, and the
community map. Its README says what each folder holds. Search it before you search the web. **Never copy it into
this repo.** Only the wiki is licensed for republishing (CC BY-SA). The others are credited and linked from the
guide, not copied, and the Dragoneers ask that their pictures not be taken.

Fandom answers scripts with 403 on article pages. Use the API instead, for example
`https://ashenempires.fandom.com/api.php?action=parse&page=<Title>&prop=wikitext&format=json`.

## Writing for the guide

- The reader has never played. Say what to do, in which order, and why, in plain sentences. Lead with the
  answer.
- Trust the sources in this order: the game's own data on what it holds, the newest patch note on rules, then
  our own play. Where sources disagree, say so on the page rather than picking one in silence. Where nobody
  knows, add a line under "What nobody could tell us" (in `guide.md`, on the Sources page) instead of guessing.
- Give a place as sextant coordinates, `x,y`. Give a level for a quest as a judgment, and mark experience
  figures as rough.
- New sources go into "How far to trust this" and "Credits".

When adding gameplay tips, research the relevant sources and make the advice actionable. For quests, verify
the names, prerequisites, NPCs, objectives, locations and rewards, recommend a useful order, and explain the
steps a player must follow. Link the supporting sources and distinguish player recommendations from verified
quest details. Resolve misleading item names and source disagreements before publishing.

## Git

- Pull before you start: `main` also gets commits from elsewhere. If a rebase conflicts in `docs/`, do not
  merge the HTML. Take either side, run `tools/build.py`, and commit the result, since `docs/` is generated from
  the merged `guide.md`.
- Commit `guide.md` together with the rebuilt `docs/`, so that what Pages serves always matches the text.
- Commit messages in this repo are a plain sentence saying what a reader gains, not a conventional-commit
  prefix.
