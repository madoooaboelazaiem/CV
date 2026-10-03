#!/usr/bin/env python3
"""Warn before publishing: phone numbers in content.json or in the CV PDF that will be embedded in a public page.

Usage: python scripts/privacy_check.py [--strict]
Prints GitHub Actions annotations (::warning) so warnings show on the workflow run. Exit 1 only with --strict.
"""
import json, os, re, sys

PHONE = re.compile(r"(?<![\w.])\+?\(?\d[\d\s().-]{7,}\d(?![\w])")
hits = []


def scan(label, text):
    for m in PHONE.finditer(text):
        raw = m.group(0).strip()
        digits = re.sub(r"\D", "", raw)
        if len(digits) >= 9 and not re.fullmatch(r"(19|20)\d{2}\D+(19|20)\d{2}", raw):
            hits.append((label, raw))


def strings(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for v in o.values():
            yield from strings(v)
    elif isinstance(o, list):
        for v in o:
            yield from strings(v)


if os.path.exists("site/content.json"):
    for s in strings(json.load(open("site/content.json", encoding="utf-8"))):
        scan("site/content.json", s)
if os.path.exists("assets/cv.pdf"):
    try:
        from pypdf import PdfReader
        for page in PdfReader("assets/cv.pdf").pages:
            scan("assets/cv.pdf (embedded in the page for the Résumé button)", page.extract_text() or "")
    except Exception as e:  # noqa
        print(f"note: could not read assets/cv.pdf ({e})")

if hits:
    for label, raw in hits:
        print(f"::warning file={label.split(' ')[0]}::Possible phone number in {label}: {raw}. Use a public CV without it, or remove assets/cv.pdf to hide the Résumé buttons.")
    print(f"{len(hits)} possible phone number(s) found. This repo is public: anyone can read them.")
    sys.exit(1 if "--strict" in sys.argv else 0)
print("privacy check: no phone numbers found")
