#!/usr/bin/env python3
"""
Build the Coronado itinerary webpage from itinerary.md.

Usage:   python3 build.py
Reads:   itinerary.md, template.html   (same folder as this script)
Writes:  Coronado_July4_2026.html

Edit itinerary.md, then re-run this script. No other steps needed.
"""

import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent

MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
}

# Country -> flag. Keys are normalized (lowercase, straight apostrophes). Add aliases freely.
FLAGS = {
    "usa": "🇺🇸", "united states": "🇺🇸", "united states of america": "🇺🇸",
    "mexico": "🇲🇽", "canada": "🇨🇦", "brazil": "🇧🇷", "argentina": "🇦🇷",
    "france": "🇫🇷", "spain": "🇪🇸", "germany": "🇩🇪", "portugal": "🇵🇹",
    "netherlands": "🇳🇱", "belgium": "🇧🇪", "croatia": "🇭🇷", "italy": "🇮🇹",
    "england": "🏴\U000e0067\U000e0062\U000e0065\U000e006e\U000e0067\U000e007f",
    "scotland": "🏴\U000e0067\U000e0062\U000e0073\U000e0063\U000e0074\U000e007f",
    "wales": "🏴\U000e0067\U000e0062\U000e0077\U000e006c\U000e0073\U000e007f",
    "japan": "🇯🇵", "south korea": "🇰🇷", "korea republic": "🇰🇷", "korea": "🇰🇷",
    "morocco": "🇲🇦", "senegal": "🇸🇳", "switzerland": "🇨🇭", "uruguay": "🇺🇾",
    "colombia": "🇨🇴", "ecuador": "🇪🇨", "paraguay": "🇵🇾", "norway": "🇳🇴",
    "sweden": "🇸🇪", "denmark": "🇩🇰", "austria": "🇦🇹", "poland": "🇵🇱",
    "ukraine": "🇺🇦", "serbia": "🇷🇸", "ghana": "🇬🇭", "algeria": "🇩🇿",
    "egypt": "🇪🇬", "nigeria": "🇳🇬", "cameroon": "🇨🇲", "tunisia": "🇹🇳",
    "ivory coast": "🇨🇮", "cote d'ivoire": "🇨🇮", "côte d'ivoire": "🇨🇮",
    "australia": "🇦🇺", "iran": "🇮🇷", "saudi arabia": "🇸🇦", "qatar": "🇶🇦",
    "cape verde": "🇨🇻", "dr congo": "🇨🇩", "democratic republic of congo": "🇨🇩",
    "congo dr": "🇨🇩", "bosnia": "🇧🇦", "bosnia and herzegovina": "🇧🇦",
    "bosnia & herzegovina": "🇧🇦", "new zealand": "🇳🇿", "costa rica": "🇨🇷",
    "panama": "🇵🇦", "jamaica": "🇯🇲", "peru": "🇵🇪", "chile": "🇨🇱",
    "venezuela": "🇻🇪", "turkey": "🇹🇷", "türkiye": "🇹🇷", "greece": "🇬🇷",
    "united kingdom": "🇬🇧", "uk": "🇬🇧", "russia": "🇷🇺",
}


def norm(s: str) -> str:
    return s.strip().lower().replace("’", "'")


def flag_for(name: str) -> str:
    return FLAGS.get(norm(name), "")


def time_to_minutes(t: str):
    """Return minutes-from-midnight for sorting, or None if not parseable."""
    s = norm(t)
    if not s or "tbd" in s:
        return None
    if "late" in s:
        return 1439
    m = re.search(r"(\d{1,2})(?::(\d{2}))?", s)
    if not m:
        return None
    hour = int(m.group(1))
    minute = int(m.group(2) or 0)
    ap = re.search(r"([ap])\.?m?", s)
    ap = ap.group(1) if ap else None
    if ap == "p" and hour != 12:
        hour += 12
    if ap == "a" and hour == 12:
        hour = 0
    return hour * 60 + minute


def fill_minutes(items):
    """Assign sort keys; unparseable (e.g. TBD) sit just before the next known time."""
    nxt = 1400.0
    for i in range(len(items) - 1, -1, -1):
        if items[i]["m"] is not None:
            nxt = items[i]["m"]
        else:
            items[i]["m"] = round(nxt - 0.01, 3)


def split_fields(s):
    return [f.strip() for f in s.split("|")]


def parse_event(item):
    f = split_fields(item)
    ev = {"t": f[0], "m": time_to_minutes(f[0]), "x": f[1] if len(f) > 1 else ""}
    if len(f) > 2:
        note = " · ".join(x for x in f[2:] if x)
        if note:
            ev["n"] = note
    return ev


def parse_match(item):
    featured = item.startswith("!")
    if featured:
        item = item[1:].strip()
    f = split_fields(item)
    time = f[0]
    matchup = f[1] if len(f) > 1 else ""
    loc = note = link = None
    for extra in f[2:]:
        if extra.startswith("@"):
            loc = extra[1:].strip()
        elif extra.startswith("http"):
            link = extra
        elif extra:
            note = (note + " · " + extra) if note else extra

    mu = matchup.strip()
    guess = mu.endswith("?")
    if guess:
        mu = mu[:-1].strip()

    d = {"t": time, "m": time_to_minutes(time)}
    parts = re.split(r"\s+vs?\s+", mu, maxsplit=1, flags=re.IGNORECASE)
    if len(parts) == 2:
        a, b = parts[0].strip(), parts[1].strip()
        d["A"] = [flag_for(a), a]
        d["B"] = [flag_for(b), b]
        if guess:
            d["g"] = True
    else:
        ro = re.sub(r"^round of 16\s*[·•:\-–—]*\s*", "", mu, flags=re.IGNORECASE).strip()
        d["ro"] = ro

    if featured:
        d["p"] = True
        d["loc"] = loc if loc else "location TBD"
    if note:
        d["n"] = note
    if link:
        d["h"] = link
    return d


def parse_markdown(text):
    meta = {}
    days = []
    cur = None
    section = None
    for raw in text.splitlines():
        s = raw.strip()
        if not s:
            continue
        if s.startswith("### "):
            name = s[4:].strip().lower()
            if "schedule" in name or "plan" in name:
                section = "sched"
            elif "world cup" in name or "match" in name or "soccer" in name:
                section = "match"
            else:
                section = None
            continue
        if s.startswith("## "):
            head = s[3:].strip()
            hl = None
            if "|" in head:
                head, hl = [p.strip() for p in head.split("|", 1)]
            cur = {"head": head, "hl": hl, "events": [], "matches": []}
            days.append(cur)
            section = None
            continue
        if s.startswith("# "):
            if cur is None and "h1" not in meta:
                meta["h1"] = s[2:].strip()
            continue  # other single-# lines are comments
        if s.startswith("- "):
            if cur is None or section is None:
                continue
            item = s[2:].strip()
            if section == "sched":
                cur["events"].append(parse_event(item))
            else:
                cur["matches"].append(parse_match(item))
            continue
        if cur is None and ":" in s:
            k, v = s.split(":", 1)
            meta[k.strip().lower()] = v.strip()
    return meta, days


def build_day(day, year):
    m = re.match(r"([A-Za-z]+),\s*([A-Za-z]+)\s+(\d+)", day["head"])
    if not m:
        raise ValueError("Bad day heading: " + day["head"])
    dow, monthname, dnum = m.group(1), m.group(2), int(m.group(3))
    month = MONTHS[monthname.lower()]
    out = {
        "id": monthname[:3].lower() + str(dnum),
        "dow": dow,
        "date": f"{monthname} {dnum}",
        "iso": f"{year}-{month:02d}-{dnum:02d}",
        "chip": f"{dow[:3]} {dnum}",
    }
    if day["hl"]:
        out["hl"] = day["hl"]
    fill_minutes(day["events"])
    fill_minutes(day["matches"])
    out["acts"] = day["events"]
    out["matches"] = day["matches"]
    return out


def main():
    md = (BASE / "itinerary.md").read_text(encoding="utf-8")
    template = (BASE / "template.html").read_text(encoding="utf-8")
    meta, days = parse_markdown(md)
    year = int(meta.get("year", "2026"))

    data = {"days": [build_day(d, year) for d in days]}
    allweek = " · ".join(x.strip() for x in meta.get("allweek", "").split(",") if x.strip())
    h1 = meta.get("h1", "Itinerary")
    sub = meta.get("subtitle", "")

    repl = {
        "__TITLE__": f"{h1} · {sub}".strip(" ·"),
        "__KICKER__": meta.get("kicker", ""),
        "__H1__": h1,
        "__SUB__": sub,
        "__DATES__": meta.get("dates", ""),
        "__TZ__": meta.get("timezone", ""),
        "__ALLWEEK__": allweek,
        "__DATA__": json.dumps(data, ensure_ascii=False),
    }
    html = template
    for k, v in repl.items():
        html = html.replace(k, v)

    out = BASE / "Coronado_July4_2026.html"
    out.write_text(html, encoding="utf-8")
    n_match = sum(len(d["matches"]) for d in data["days"])
    n_act = sum(len(d["acts"]) for d in data["days"])
    print(f"Built {out.name}: {len(data['days'])} days, {n_act} schedule items, {n_match} matches.")


if __name__ == "__main__":
    main()
