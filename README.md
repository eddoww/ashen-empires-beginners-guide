# A beginner's route through Ashen Empires

**Read it here: https://eddoww.github.io/ashen-empires-beginners-guide/**

From the beach of Valinor to about level 30: what to do, in which order, and why, for each of the three towns a
new character can go to after Valinor (Krog, Silvest, Whisperdale), and what comes after. Every quest links to its
walkthrough on AE Guides and on the wiki, and shows the pictures those walkthroughs have.

## What is in here

| | |
|---|---|
| `guide.md` | The whole guide, as one text. This is the file to edit |
| `tools/build.py` | Cuts `guide.md` into the twelve pages under `docs/` |
| `tools/collect_images.py`, `tools/fetch_images.py` | Find the pictures each quest's walkthroughs show, download them, shrink them |
| `images/manifest.json` | Which picture belongs to which quest, where it comes from, who uploaded it |
| `data/wiki_pages.json` | Which wiki page describes which quest |
| `docs/` | The site as GitHub Pages serves it |

## Changing the guide

Edit `guide.md`, then:

```sh
pip install markdown
python3 tools/build.py
```

A table whose first column is headed "Quest" gets, for each row, the links and pictures of the quest it names.
A block like this in the text becomes a row of pictures:

```
::: pictures
aeguides Images/Maps/Dawat.png | Dawat | https://bofur24.github.io/AEGuides/highlands.html
wiki Portal.jpg | A granite portal | General_Gameplay
:::
```

After adding a quest or a picture block, fetch the pictures again (needs ImageMagick). The first script reads
pages of the two sources that were downloaded beforehand: AE Guides' five `.html` pages in one folder, and the
wiki's pages as `<Title>.wiki` in another.

```sh
python3 tools/collect_images.py <AE Guides pages> <wiki pages> data/wiki_pages.json
python3 tools/fetch_images.py
python3 tools/build.py
```

Corrections are welcome: open an issue or a pull request against `guide.md`. The guide lists what it does not
know under "What nobody could tell us".

## Whose work this is

- **[AE Guides](https://bofur24.github.io/AEGuides)** by Keith Heffington (bofur24): the walk through every quest
  of Valinor, the three starting regions and the Highlands, and most of the pictures shown here. Its repository
  declares no license. The pictures are shown with credit and a link back to the quest they come from, and will
  be taken down if their author asks.
- **[Ashen Empires Wiki](https://ashenempires.fandom.com)** and its editors: a page for most quests, the patch
  notes, and the rest of the pictures. Text and pictures there are licensed CC BY-SA; each picture here names its
  uploader.
- **[AE Database](https://www.aedatabase.com)** and its contributors: the bestiary and the list of quest rewards.
- **The [interactive map](https://gork3n.github.io/ashen-empires-map/openlayers.html)** by gork3n and Sir Chris.
- **Ashen Empires** is the work of Iron Will Games. Every name, quest and picture of the game is theirs. This is
  a players' guide and is not affiliated with them.
