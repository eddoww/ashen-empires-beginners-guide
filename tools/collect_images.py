#!/usr/bin/env python3
"""Write images/manifest.json: for each quest the guide names, the pictures its two walkthroughs show.

    tools/collect_images.py <AE Guides pages dir> <wiki pages dir> <walkthrough links json>

The first two are folders of pages fetched beforehand (AE Guides' five .html pages; the wiki's pages as
<Title>.wiki). The third lists, per quest name, the address of its AE Guides block and of its wiki page.
Nothing is downloaded here; tools/fetch_images.py does that from the manifest.
"""
import html, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
AEG_REV = "74d143ff02aa8bfed69aca38ffd5bea8673fd3f0"
AEG_RAW = "https://raw.githubusercontent.com/bofur24/AEGuides/%s/" % AEG_REV
AEG_SITE = "https://bofur24.github.io/AEGuides/"
WIKI = "https://ashenempires.fandom.com/wiki/"

# The guide calls a quest what the game calls it; the wiki often files it under somebody's name.
WIKI_PAGE = {
    "Welcome To Ashen Empires": "Valinor_Island", "Our Little Spider Problem": "Our_Little_Spider_Problem",
    "Strange Fascination": "Bat_Ear_Necklace", "The Necklace": "Triddle_Shell_Armor",
    "The Alchemist's Apprentice": "Alchemist_Baki", "Curtis's Secret": "Curtis_s_Secret",
    "The Ring": "Sarah_s_Promise_Ring", "A Goblin Problem": "Supply_Crates", "Ancient Magic": "Crazy_Hermit",
    "Formidable Formicidae": "40_Fire_Ants", "Swamped": "Rumpda_s_Swamp_Quest", "Leonard is Lost": "Oonga_s_Lost_Pet",
    "Tree Trouble": "Afflicted_Tree", "Protect Krog!": "Warrog", "Great Disrepair": "Krog_Sewers",
    "Reclaiming What's Mine": "Ivogur", "Payment in Full": "Kobold_Chief", "Favorable Dealings": "Krog_Arda_Quest",
    "Warrior of Krog": "Patron_Quests", "Knight of Silvest": "Patron_Quests", "Knight of Whisperdale": "Patron_Quests",
    "Nest of Pests": "Howard_Kaps", "The Wrong Crowd": "Howard_Kaps", "Something's Bugging Sozal": "Sozal_Cave",
    "The Lake": "Karter_Jons_Kobold_Quest", "The Fort": "Karter_Jons_Kobold_Quest", "Join Forces": "Silvest_Sword_Quest",
    "Juicy": "Schrute", "Of Kobolds": "Of_Kobolds", "Women and Ale": "Pirate_Quelling_Quest",
    "Foul Beasts": "Warg_Quest", "A Shadow Roams the Lands": "Varios", "Time for Revenge": "Varios",
    "Correspondence": "Jarkam_s_Note", "Friend of the Earth": "Kudah", "Hero of Dawat": "Shargar",
    "Sweet Relief": "Sweetness", "Haunted House": "Dawat_Worker", "Pegi's Picnic": "Pegis_Picnic",
    "Maid Nelly's Locket": "Maid_Nelly", "Minotaur Ambush": "Ragged_Traveller", "Shovel Trouble": "Jenn_Talbot_s_Shovel",
    "Valekar's Fortress": "Valekar_s_Fortress", "Treasures": "Hapuna", "The Parian Warlords": "Parian_Warlords",
    "The Wisdom of Wizards": "The_Wisdom_of_Wizards", "The Art of Combat": "The_Art_of_Combat",
    "War": "War", "Proof": "Proof", "Honor in Battle": "The_Art_of_Combat", "Gem Thieves": "Gem_Thieves",
}
# AE Guides' own headings where they differ from the game's name.
AEG_NAME = {"Disciple of the Mind": "Disciple of Mind", "Lift Their Spirits": "Lift Their Spirts",
            "Farming Training": "Farming Trainer"}
DULL = re.compile(r"(^|/)(gold|exp|experience|faction|epool|xp)[^/]*\.(png|jpg)$", re.I)


def norm(text):
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def guide_quests():
    """The quest named in the first cell of every row of every table headed "Quest"."""
    names, in_table = [], False
    for line in open(os.path.join(ROOT, "guide.md"), encoding="utf-8"):
        if not line.startswith("|"):
            in_table = False
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells[0] == "Quest":
            in_table = True
        elif in_table and not set(cells[0]) <= set("-: "):
            name = re.sub(r"\*\*", "", cells[0])
            name = re.split(r", (?:and|first|the|last|to its)\b", name)[0].strip()
            if name and name not in names:
                names.append(name)
    return names


def aeg_blocks(folder):
    """Each quest block of the AE Guides pages: title -> (page, anchor, [(src, alt, kind)])."""
    out = {}
    for page in sorted(os.listdir(folder)):
        if not page.endswith(".html") or page in ("index.html", "quest.html"):
            continue
        text = open(os.path.join(folder, page), encoding="utf-8", errors="replace").read()
        spots = []
        for found in re.finditer(r'<h2[^>]*\bid="([^"]+)"[^>]*>([\s\S]*?)</h2>', text):
            title = html.unescape(re.sub(r"<[^>]+>", "", found.group(2))).strip()
            if title:
                spots.append((found.start(), found.group(1), title))
        spots.sort()
        for at, (start, anchor, title) in enumerate(spots):
            block = text[start:spots[at + 1][0] if at + 1 < len(spots) else len(text)]
            pics, seen = [], set()
            for tag in re.findall(r"<img\b[^>]*>", block):
                src = re.search(r'src="([^"]+)"', tag)
                alt = re.search(r'alt="([^"]*)"', tag)
                kind = re.search(r'class="([^"]+)"', tag)
                if not src or DULL.search(src.group(1)) or src.group(1) in seen:
                    continue
                seen.add(src.group(1))
                pics.append((src.group(1), html.unescape(alt.group(1)) if alt else "", kind.group(1) if kind else ""))
                # A reward's thumbnail opens the item's tooltip, a second picture.
                tip = re.search(r"popover-img' src='([^']+)'", html.unescape(tag))
                if tip and tip.group(1) not in seen:
                    seen.add(tip.group(1))
                    pics.append((tip.group(1), (html.unescape(alt.group(1)) if alt else "") + " (tooltip)", "tooltip"))
            out.setdefault(norm(title), (page, anchor, pics))
    return out


def wiki_page(folder, title, depth=0):
    path = os.path.join(folder, re.sub(r"[^A-Za-z0-9._-]+", "_", title) + ".wiki")
    if not os.path.exists(path):
        return None, []
    text = open(path, encoding="utf-8").read()
    turn = re.search(r"#REDIRECT\s*\[\[([^\]|#]+)", text, re.I)
    if turn and depth < 3:
        return wiki_page(folder, turn.group(1).strip(), depth + 1)
    real = re.match(r"<!-- (.*?) \|", text)
    pics = []
    for name, rest in re.findall(r"\[\[File:([^|\]]+)([^\]]*)\]\]", text):
        name = name.strip()
        if name.lower() in ("ae exp.png", "soc exp.png", "tr exp.png", "tof exp.png"):
            continue
        words = [w for w in rest.split("|") if w and not re.match(r"^(thumb|right|left|center|none|\d+px|x\d+px|frame|link=.*)$", w.strip())]
        caption = words[-1].strip() if words else os.path.splitext(name)[0]
        if name not in [p[0] for p in pics]:
            pics.append((name, caption))
    return (real.group(1) if real else title), pics


def prose_pictures():
    """The pictures the guide's own text asks for, in its "::: pictures" blocks.

    A line is "aeguides <path in its repository> | caption | page" or "wiki <file name> | caption | page title".
    """
    out, inside = [], False
    for line in open(os.path.join(ROOT, "guide.md"), encoding="utf-8"):
        line = line.strip()
        if line == "::: pictures":
            inside = True
        elif line == ":::":
            inside = False
        elif inside and line:
            source, rest = line.split(" ", 1)
            what, caption, page = [part.strip() for part in rest.split("|")]
            if source == "aeguides":
                out.append({"from": "aeguides", "url": AEG_RAW + what.replace(" ", "%20"), "caption": caption,
                            "kind": "prose", "page": page})
            else:
                out.append({"from": "wiki", "file": what, "caption": caption, "page": WIKI + page})
    return out


def main():
    aeg_dir, wiki_dir, links_path = sys.argv[1:4]
    links = {q["name"]: q for q in json.load(open(links_path, encoding="utf-8"))["quests"]}
    blocks = aeg_blocks(aeg_dir)
    quests = {}
    for name in guide_quests():
        entry = {"aeguides": None, "wiki": None, "pictures": []}
        block = blocks.get(norm(AEG_NAME.get(name, name)))
        if block:
            page, anchor, pics = block
            entry["aeguides"] = AEG_SITE + page + "#" + anchor
            for src, alt, kind in pics:
                entry["pictures"].append({"from": "aeguides", "url": AEG_RAW + src.replace(" ", "%20"),
                                          "caption": alt, "kind": kind, "page": entry["aeguides"]})
        title = WIKI_PAGE.get(name) or (links.get(name, {}).get("wiki") or {}).get("title") or name
        real, pics = wiki_page(wiki_dir, title)
        if real:
            entry["wiki"] = WIKI + real.replace(" ", "_")
            for file, caption in pics:
                entry["pictures"].append({"from": "wiki", "file": file, "caption": caption, "page": entry["wiki"]})
        quests[name] = entry
    os.makedirs(os.path.join(ROOT, "images"), exist_ok=True)
    json.dump({"quests": quests, "extra": prose_pictures()}, open(os.path.join(ROOT, "images", "manifest.json"), "w"), indent=1)
    lone = [n for n, e in quests.items() if not e["aeguides"] and not e["wiki"]]
    print(len(quests), "quests,", sum(len(e["pictures"]) for e in quests.values()), "pictures")
    print("neither guide has:", lone)
    print("no pictures:", [n for n, e in quests.items() if not e["pictures"]])


main()
