#!/usr/bin/env python3
"""Write the site under docs/ from guide.md and images/manifest.json.

    tools/build.py

guide.md is the whole guide as one text. It is cut into pages at its second-level headings (PAGES says which
heading goes on which page). Every row of a table headed "Quest" gets the links to that quest's walkthroughs
and, folded away under it, the pictures those walkthroughs show. A "::: pictures" block in the text becomes a
row of pictures. Needs the Python package "markdown".
"""
import html
import json
import os
import re

import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs")
TITLE = "Ashen Empires: a beginner's route"

# file name, name in the menu, the guide's second-level headings that go on it ("" is what precedes the first)
PAGES = [
    ("index", "Start here", ["", "The route in one page", "Before you start: build and town"]),
    ("valinor", "Valinor, level 1 to 10", ["Valinor, level 1 to 10"]),
    ("mainland", "Arriving on the mainland", ["Your first ten minutes on the mainland",
                                              "The patron: your main source of levels"]),
    ("krog", "Krog", ["Krog and the Black Swamp"]),
    ("silvest", "Silvest", ["Silvest and the Silvest Valley"]),
    ("whisperdale", "Whisperdale", ["Whisperdale and the Darkwoods"]),
    ("gear", "Portal trips and gear", ["Worth a portal trip, whichever town you chose",
                                       "What to wear from level 8 to 25"]),
    ("after", "After level 25", ["After your starting region"]),
    ("basics", "Things to know", ["Things a beginner has to know"]),
    ("about", "Sources and credits", ["How far to trust this", "What nobody could tell us", "Credits"]),
]

SOURCE = {"aeguides": "AE Guides", "wiki": "Ashen Empires Wiki"}


def strip(text):
    return html.unescape(re.sub(r"<[^>]+>", "", text)).strip()


def quest_key(cell):
    """The quest a table's first cell names: "War, the goblins" and "Honor in Battle, and five more" are one each."""
    return re.split(r", (?:and|first|the|last|to its)\b", strip(cell))[0].strip()


def figure(picture):
    caption = picture.get("caption") or ""
    credit = SOURCE[picture["from"]]
    if picture.get("by"):
        credit += ", uploaded by " + picture["by"] + ", CC BY-SA"
    return ('<a class="pic" href="img/%s.webp" data-credit="%s" data-page="%s" title="%s">'
            '<img loading="lazy" src="img/%s.t.webp" alt="%s"><span>%s</span><i>%s</i></a>') % (
        picture["key"], html.escape(credit, True), html.escape(picture["page"], True), html.escape(caption, True),
        picture["key"], html.escape(caption, True), html.escape(caption), SOURCE[picture["from"]].split(" ")[0]
        if picture["from"] == "aeguides" else "Wiki")


def prose_galleries(text, extra):
    """Each "::: pictures" block of the guide -> a row of pictures, taken in order from the manifest's extras."""
    at = [0]

    def gallery(block):
        lines = [line for line in block.group(1).strip().split("\n") if line.strip()]
        mine = extra[at[0]:at[0] + len(lines)]
        at[0] += len(lines)
        row = "".join(figure(p) for p in mine if not p.get("missing")).replace(' loading="lazy"', "")
        return '\n<div class="pics prose">%s</div>\n' % row

    return re.sub(r"^::: pictures\n([\s\S]*?)\n:::$", gallery, text, flags=re.M)


def quest_tables(body, page, quests, index):
    """Give each quest row its links and its pictures, and note it for the search."""

    def table(found):
        whole = found.group(0)
        heads = re.findall(r"<th[^>]*>([\s\S]*?)</th>", whole)
        if not heads or strip(heads[0]) != "Quest":
            return '<div class="tw">%s</div>' % whole
        level_at = next((i for i, h in enumerate(heads) if strip(h) == "Level"), None)

        def row(found_row):
            cells = re.findall(r"<td[^>]*>([\s\S]*?)</td>", found_row.group(1))
            if not cells:
                return found_row.group(0)
            name = quest_key(cells[0])
            anchor = "q-" + re.sub(r"[^a-z0-9]+", "-", strip(cells[0]).lower()).strip("-")
            while anchor in seen:
                anchor += "-"
            seen.add(anchor)
            index.append({"n": strip(cells[0]), "p": page, "a": anchor,
                          "l": strip(cells[level_at]) if level_at is not None else ""})
            quest = quests.get(name)
            links, pictures = "", ""
            if quest:
                where = [(quest.get("aeguides"), "AE Guides"), (quest.get("wiki"), "Wiki")]
                links = " · ".join('<a href="%s">%s</a>' % (html.escape(u, True), t) for u, t in where if u)
                shown = [p for p in quest["pictures"] if not p.get("missing")]
                if shown:
                    pictures = ('<tr class="pr"><td colspan="%d"><details><summary>%d pictures of %s</summary>'
                                '<div class="pics">%s</div></details></td></tr>') % (
                        len(cells), len(shown), html.escape(name), "".join(figure(p) for p in shown))
            first = cells[0] + ('<span class="src">%s</span>' % links if links else "")
            rest = "".join("<td>%s</td>" % c for c in cells[1:])
            return '<tr id="%s"><td>%s</td>%s</tr>%s' % (anchor, first, rest, pictures)

        return '<div class="tw">%s</div>' % re.sub(r"<tr>([\s\S]*?)</tr>", row, whole)

    seen = set()
    return re.sub(r"<table>[\s\S]*?</table>", table, body)


def cut(whole):
    """The guide's HTML as {second-level heading: its part}, "" being what comes before the first."""
    parts, marks = {}, list(re.finditer(r'<h2 id="([^"]+)">([\s\S]*?)</h2>', whole))
    parts[""] = whole[:marks[0].start()] if marks else whole
    for at, mark in enumerate(marks):
        parts[strip(mark.group(2))] = whole[mark.start():marks[at + 1].start() if at + 1 < len(marks) else len(whole)]
    return parts


def layout(page, title, body, sections, older, newer, credits_line):
    menu = []
    for name, label, _ in PAGES:
        here = name == page
        menu.append('<li%s><a href="%s.html">%s</a>' % (' class="here"' if here else "", name, label))
        if here and sections:
            menu.append("<ul>%s</ul>" % "".join('<li class="l%d"><a href="#%s">%s</a></li>' % s for s in sections))
        menu.append("</li>")
    step = ""
    if older:
        step += '<a class="older" href="%s.html">&larr; %s</a>' % older
    if newer:
        step += '<a class="newer" href="%s.html">%s &rarr;</a>' % newer
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s - %(site)s</title>
<meta name="description" content="A beginner's route through Ashen Empires: Valinor, then Krog, Silvest or Whisperdale, quest by quest.">
<link rel="stylesheet" href="style.css">
</head>
<body>
<header>
<button id="menu" aria-label="Menu">&#9776;</button>
<a class="site" href="index.html">%(site)s</a>
<div class="find"><input id="find" type="search" placeholder="Find a quest..." autocomplete="off"><ul id="found"></ul></div>
</header>
<div class="frame">
<nav id="nav"><ul>%(menu)s</ul></nav>
<main>
%(head)s%(body)s
<p class="step">%(step)s</p>
<footer>%(credits)s</footer>
</main>
</div>
<div id="box" hidden><button id="shut" aria-label="Close">&times;</button><button id="prev" aria-label="Previous">&lsaquo;</button><img alt=""><button id="next" aria-label="Next">&rsaquo;</button><p></p></div>
<script src="quests.js"></script>
<script src="app.js"></script>
</body>
</html>
""" % {"title": html.escape(title), "site": TITLE, "menu": "".join(menu), "body": body, "step": step,
       "credits": credits_line,
       "head": "" if body.lstrip().startswith("<h2") else "<h1>%s</h1>\n" % html.escape(title)}


def main():
    manifest = json.load(open(os.path.join(ROOT, "images", "manifest.json"), encoding="utf-8"))
    text = open(os.path.join(ROOT, "guide.md"), encoding="utf-8").read()
    text = re.sub(r"^# .*\n", "", text, count=1)  # each page has its own title
    text = prose_galleries(text, manifest.get("extra", []))
    whole = markdown.markdown(text, extensions=["tables", "toc", "sane_lists"])
    whole = whole.replace("<li>[ ] ", '<li class="tick"><input type="checkbox"> ')
    whole = re.sub(r"<ul>\s*(?=<li class=\"tick\">)", '<ul class="ticks">', whole)
    parts = cut(whole)

    unplaced = set(parts) - {h for _, _, heads in PAGES for h in heads}
    if unplaced:
        raise SystemExit("no page takes: %s" % sorted(unplaced))
    home = {}  # heading id -> the page it is on
    for name, _, heads in PAGES:
        for head in heads:
            for anchor in re.findall(r'<h[2-4] id="([^"]+)"', parts[head]):
                home[anchor] = name

    pictures = [p for q in manifest["quests"].values() for p in q["pictures"]] + manifest.get("extra", [])
    shown = {p["key"]: p for p in pictures if not p.get("missing")}
    count = {s: len([p for p in shown.values() if p["from"] == s]) for s in SOURCE}
    people = sorted({p["by"] for p in shown.values() if p.get("by")})
    credits_line = ('Ashen Empires is the work of Iron Will Games. Pictures: <a href="https://bofur24.github.io/AEGuides">'
                    'AE Guides</a> and the <a href="https://ashenempires.fandom.com">Ashen Empires Wiki</a> (CC BY-SA). '
                    '<a href="about.html#credits">Credits</a>.')
    tally = ("<p>These pages show %d pictures from AE Guides and %d from the wiki, the latter uploaded there by %s. "
             "Each opens with its source named and linked.</p>") % (count["aeguides"], count["wiki"], ", ".join(people))

    index = []
    for at, (name, label, heads) in enumerate(PAGES):
        body = "".join(parts[h] for h in heads)
        if name == "about":
            body += tally
        body = re.sub(r'href="#([^"]+)"',
                      lambda m: 'href="%s#%s"' % ("" if home.get(m.group(1), name) == name else home[m.group(1)] + ".html",
                                                  m.group(1)), body)
        body = quest_tables(body, name, manifest["quests"], index)
        sections = [(int(level), anchor, strip(title)) for level, anchor, title in
                    re.findall(r'<h([23]) id="([^"]+)">([\s\S]*?)</h\1>', body)]
        for level, anchor, title in sections:
            index.append({"n": title, "p": name, "a": anchor, "l": "", "h": 1})
        older = (PAGES[at - 1][0], PAGES[at - 1][1]) if at else None
        newer = (PAGES[at + 1][0], PAGES[at + 1][1]) if at + 1 < len(PAGES) else None
        page = layout(name, label if name != "index" else "A beginner's route through Ashen Empires", body, sections,
                      older, newer, credits_line)
        with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as file:
            file.write(page)
    with open(os.path.join(OUT, "quests.js"), "w", encoding="utf-8") as file:
        file.write("var QUESTS=%s;\n" % json.dumps(index, separators=(",", ":")))
    open(os.path.join(OUT, ".nojekyll"), "w").close()
    used = {key for key in shown}
    stray = [f for f in os.listdir(os.path.join(OUT, "img")) if f.split(".")[0] not in used]
    for name in stray:
        os.remove(os.path.join(OUT, "img", name))
    print(len(PAGES), "pages,", len([i for i in index if not i.get("h")]), "quest rows,", len(shown), "pictures,",
          len(stray), "stray files removed")


main()
