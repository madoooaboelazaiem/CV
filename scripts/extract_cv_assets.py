#!/usr/bin/env python3
"""Pull what a CV PDF already contains: text, hyperlinks and the embedded photo.

Usage: python extract_cv_assets.py cv.pdf outdir/
Writes: outdir/cv.txt, outdir/links.json, outdir/photo.png (with transparency if the PDF had a soft mask)
Needs: poppler-utils (pdftotext, pdfimages), pypdf, Pillow
"""
import glob, json, os, subprocess, sys
from PIL import Image
from pypdf import PdfReader

pdf, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
subprocess.run(["pdftotext", "-layout", pdf, os.path.join(out, "cv.txt")], check=False)

links = []
for page in PdfReader(pdf).pages:
    for an in page.get("/Annots") or []:
        o = an.get_object(); act = o.get("/A")
        if act and "/URI" in act:
            links.append(str(act["/URI"]))
json.dump(links, open(os.path.join(out, "links.json"), "w"), indent=2)

tmp = os.path.join(out, "_img")
subprocess.run(["pdfimages", "-png", pdf, tmp], check=False)
lst = subprocess.run(["pdfimages", "-list", pdf], capture_output=True, text=True).stdout.splitlines()[2:]
files = sorted(glob.glob(tmp + "-*.png"))
photo = None
for i, line in enumerate(lst):
    cols = line.split()
    if len(cols) > 2 and cols[2] == "image" and i < len(files):
        im = Image.open(files[i]).convert("RGBA")
        if i + 1 < len(lst) and lst[i + 1].split()[2] == "smask" and i + 1 < len(files):
            im.putalpha(Image.open(files[i + 1]).convert("L").resize(im.size))
        if photo is None or im.width * im.height > photo.width * photo.height:
            photo = im
if photo:
    photo.save(os.path.join(out, "photo.png"))
for f in files:
    os.remove(f)
print(json.dumps({"text": os.path.join(out, "cv.txt"), "links": links, "photo": bool(photo),
                  "photo_size": photo.size if photo else None}, indent=2))
if photo and photo.width < 300:
    print("note: embedded photo is small; ask for a higher-resolution portrait for the hero.")
