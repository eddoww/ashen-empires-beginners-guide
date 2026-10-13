#!/usr/bin/env python3
"""Download the pictures images/manifest.json names and write them, shrunk, under docs/img.

    tools/fetch_images.py [cache_dir]

Each picture is kept as it came in cache_dir (default: .cache) so that a second run downloads nothing. Under
docs/img it becomes a WebP of at most 1400 pixels across and a thumbnail of at most 240 high. The manifest gets,
per picture, where those two are, their size and, for the wiki's, who uploaded it. Needs ImageMagick ("magick").
"""
import hashlib, json, os, re, subprocess, sys, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, ".cache")
OUT = os.path.join(ROOT, "docs", "img")
AGENT = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) ashen-empires-beginners-guide"}
API = "https://ashenempires.fandom.com/api.php?"


def get(url):
    # The wiki's picture host only answers a request that says it comes from the wiki.
    headers = dict(AGENT, Referer="https://ashenempires.fandom.com/") if "wikia.nocookie.net" in url else AGENT
    return urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60).read()


def wiki_files(names):
    """File name -> (address, uploader), asked of the wiki fifty at a time."""
    found = {}
    names = sorted(names)
    for at in range(0, len(names), 40):
        query = urllib.parse.urlencode({"action": "query", "prop": "imageinfo", "iiprop": "url|user", "format": "json",
                                        "titles": "|".join("File:" + n for n in names[at:at + 40])})
        answer = json.loads(get(API + query))["query"]
        back = {n["to"]: n["from"] for n in answer.get("normalized", [])}
        for page in answer["pages"].values():
            info = page.get("imageinfo")
            if info:
                asked = back.get(page["title"], page["title"])[len("File:"):]
                found[asked] = (info[0]["url"], info[0].get("user", ""))
        time.sleep(1)
    return found


def fetch(job):
    url, raw = job
    if not os.path.exists(raw):
        try:
            data = get(url)
        except Exception as error:  # a picture the source no longer has
            return url, str(error)
        with open(raw, "wb") as file:
            file.write(data)
    return url, None


def shrink(raw, key):
    full, thumb = os.path.join(OUT, key + ".webp"), os.path.join(OUT, key + ".t.webp")
    if not os.path.exists(full):
        subprocess.run(["magick", raw + "[0]", "-resize", "1400x1400>", "-quality", "82", full], check=True)
    if not os.path.exists(thumb):
        subprocess.run(["magick", raw + "[0]", "-resize", "360x240>", "-quality", "78", thumb], check=True)
    size = subprocess.run(["magick", "identify", "-format", "%w %h", full], capture_output=True, text=True).stdout.split()
    return int(size[0]), int(size[1])


def main():
    os.makedirs(CACHE, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(ROOT, "images", "manifest.json")
    manifest = json.load(open(path, encoding="utf-8"))
    pictures = [p for q in manifest["quests"].values() for p in q["pictures"]] + manifest.get("extra", [])
    wiki = wiki_files({p["file"] for p in pictures if p["from"] == "wiki"})
    jobs = {}
    for p in pictures:
        p.pop("missing", None)  # what an earlier run could not get is tried again
        if p["from"] == "wiki":
            if p["file"] not in wiki:
                p["missing"] = True
                continue
            p["url"], p["by"] = wiki[p["file"]]
        ending = os.path.splitext(urllib.parse.urlparse(p["url"]).path.split("/revision/")[0])[1].lower() or ".png"
        p["key"] = p["from"][0] + hashlib.sha1(p["url"].split("/revision/")[0].encode()).hexdigest()[:12]
        jobs[p["url"]] = os.path.join(CACHE, p["key"] + ending)
    with ThreadPoolExecutor(4) as pool:
        failed = {url: why for url, why in pool.map(fetch, jobs.items()) if why}
    for p in pictures:
        if p.get("missing") or p["url"] in failed:
            p["missing"] = True
            continue
        try:
            p["w"], p["h"] = shrink(jobs[p["url"]], p["key"])
            p.pop("missing", None)
        except Exception as error:
            p["missing"] = True
            failed[p["url"]] = str(error)
    json.dump(manifest, open(path, "w"), indent=1)
    print(len(jobs), "pictures,", len(failed), "failed")
    for url, why in list(failed.items())[:20]:
        print("  ", url, why)


main()
