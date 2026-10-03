#!/usr/bin/env python3
"""Check content.json before building. Fails (exit 1) on mistakes that would break the
page; prints warnings for things that are probably unintended.

Usage: python scripts/validate_content.py [site/content.json]
On GitHub Actions the messages also appear as annotations on the file.
"""
import json, os, re, sys

path = sys.argv[1] if len(sys.argv) > 1 else "site/content.json"
GH = os.environ.get("GITHUB_ACTIONS") == "true"
errors, warns = [], []

def err(m): errors.append(m); print(f"::error file={path}::{m}" if GH else f"  ERROR  {m}")
def warn(m): warns.append(m); print(f"::warning file={path}::{m}" if GH else f"  warn   {m}")

try:
    c = json.load(open(path, encoding="utf-8"))
except json.JSONDecodeError as e:
    err(f"Not valid JSON: {e.msg} at line {e.lineno}, column {e.colno}. Usual causes: a missing comma, a trailing comma, or an unescaped \" inside text.")
    sys.exit(1)

SECTIONS = {"ai", "skills", "work", "systems", "experience", "learning", "achievements", "contact"}
KNOWN = SECTIONS | {"meta", "person", "nav", "hero", "marquee", "about", "footer"}
for k in c:
    if k not in KNOWN: warn(f'Unknown top-level key "{k}" (ignored by the site). Typo?')

def need(obj, key, where):
    if not isinstance(obj, dict) or not obj.get(key): err(f'{where}.{key} is missing or empty'); return False
    return True

def heading(sec):
    h = c.get(sec, {}).get("heading")
    if not (isinstance(h, list) and len(h) == 2 and all(isinstance(x, str) and x for x in h)):
        err(f'{sec}.heading must be two strings, e.g. ["Things I\'ve", "built."]')

need(c.get("person", {}), "name", "person"); need(c.get("hero", {}), "titleLines", "hero")
tl = c.get("hero", {}).get("titleLines", [])
if not (isinstance(tl, list) and 1 <= len(tl) <= 3): err("hero.titleLines must be a list of 1-3 short lines")
need(c.get("about", {}), "paragraphs", "about")
for l in c.get("person", {}).get("links", []):
    if not re.match(r"^(https?://|mailto:)", l.get("url", "")): err(f'person.links: "{l.get("label")}" needs a url starting with https://')
if not c.get("person", {}).get("email"): warn("person.email is empty: the contact section has no address")

for s in SECTIONS & set(c):
    if s != "contact" or "heading" in c[s]: heading(s)

if "skills" in c:
    cats = [x[0] for x in c["skills"].get("categories", [])]
    if not cats or cats[0] != "all": err('skills.categories must start with ["all","All"]')
    seen = {}
    for i, it in enumerate(c["skills"].get("items", [])):
        w = f'skills.items[{i}] ({it.get("name","?")})'
        for k in ("sym", "name", "cat"):
            if not it.get(k): err(f"{w}: missing {k}")
        if it.get("cat") not in cats: err(f'{w}: cat "{it.get("cat")}" is not in skills.categories')
        if len(it.get("sym", "")) > 2: warn(f'{w}: sym "{it.get("sym")}" is longer than 2 characters and will look cramped')
        if it.get("sym") in seen: warn(f'{w}: sym "{it.get("sym")}" is already used by {seen[it["sym"]]}')
        seen[it.get("sym")] = it.get("name")
    if len(c["skills"].get("items", [])) > 70: warn("More than 70 skills: the periodic table gets crowded")

if "work" in c:
    for i, p in enumerate(c["work"].get("projects", [])):
        w = f'work.projects[{i}]'
        for k in ("title", "description"):
            if not p.get(k): err(f"{w}: missing {k}")
        if not 1 <= len(p.get("points", [])) <= 5: warn(f'{w} ({p.get("title")}): aim for 2-4 points')
    if not c["work"].get("projects"): err("work.projects is empty (delete the work key to hide the section)")

if "experience" in c:
    for i, x in enumerate(c["experience"].get("items", [])):
        for k in ("year", "role", "org"):
            if not x.get(k): err(f"experience.items[{i}]: missing {k}")

if "achievements" in c:
    for i, a in enumerate(c["achievements"].get("items", [])):
        if "big" not in a and not isinstance(a.get("value"), (int, float)):
            err(f'achievements.items[{i}]: needs either "big" (text) or a numeric "value"')
        if not a.get("title"): err(f"achievements.items[{i}]: missing title")

if "systems" in c:
    for i, s in enumerate(c["systems"].get("items", [])):
        if not (2 <= len(s.get("nodes", [])) <= 8): warn(f'systems.items[{i}] ({s.get("name")}): use 4-6 nodes')

for k, v in c.get("nav", {}).items():
    if k not in c and k != "contact": warn(f'nav.{k} points to a section that does not exist')

print(f"content check: {len(errors)} error(s), {len(warns)} warning(s)")
sys.exit(1 if errors else 0)
