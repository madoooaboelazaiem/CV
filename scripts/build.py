#!/usr/bin/env python3
"""Build a single-file CV portfolio site from content.json + images.

Usage:
  python build.py --content content.json --out index.html \
      [--photo portrait.png] [--avatar avatar.png] [--card card.png] [--cv cv.pdf] \
      [--cutout] [--template ../assets/template.html]

--photo   Real portrait. Needs transparency (a cutout). Used for the halftone hero.
--avatar  3D/animated character. Shown inside the scratch-reveal with cursor look-at.
--card    Small photo for the ID card (defaults to --photo).
--cv      PDF offered by every "Résumé" button. Omit to hide those buttons.
--url     Full public URL of this page (canonical + og:url). Optional.
--og-image  Absolute URL of the 1280x640 link-preview image. Optional.
--cutout  Remove backgrounds with rembg for any image without transparency.
--theme   editorial (default: halftone + scratch reveal) or sketch (sketchbook:
          the avatar draws itself in pencil, then colours in; needs --avatar).
Requires: Pillow, numpy. --cutout also needs: pip install rembg onnxruntime
"""
import argparse, base64, html, io, json, os, sys
import numpy as np
from PIL import Image, ImageChops, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FIG_W, FIG_H = 429, 504  # hero figure box (matches CSS aspect-ratio)


def has_alpha(im):
    if im.mode not in ("RGBA", "LA"):
        return False
    lo, _ = im.getchannel("A").getextrema()
    return lo < 250


def cutout(im):
    try:
        from rembg import remove, new_session
    except ImportError:
        sys.exit("--cutout needs: pip install rembg onnxruntime")
    return remove(im, session=new_session("isnet-general-use")).convert("RGBA")


def load(path, want_cut):
    im = Image.open(path)
    im = im.convert("RGBA")
    if want_cut and not has_alpha(im):
        print(f"  removing background: {os.path.basename(path)}")
        im = cutout(im)
    return im


def to_uri(im, q=82):
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=q, method=6)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()


def fit_portrait(im):
    """Fit a cutout into the 429x504 hero box, bottom-centred, transparent padding."""
    bbox = im.getbbox() or (0, 0, im.width, im.height)
    im = im.crop(bbox)
    scale = min(FIG_W * 2 / im.width, FIG_H * 2 / im.height)
    im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.LANCZOS)
    box = Image.new("RGBA", (FIG_W * 2, FIG_H * 2), (0, 0, 0, 0))
    box.alpha_composite(im, ((box.width - im.width) // 2, box.height - im.height))
    return box.resize((FIG_W, FIG_H), Image.LANCZOS)


def fit_avatar(im):
    bbox = im.getbbox() or (0, 0, im.width, im.height)
    im = im.crop(bbox)
    w = 640
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)


def fit_card(im):
    bg = Image.new("RGBA", im.size, (233, 226, 212, 255))
    bg.alpha_composite(im)
    im = bg.convert("RGB")
    tw, th = 286, 336
    s = max(tw / im.width, th / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    l, t = (im.width - tw) // 2, 0
    return im.crop((l, t, l + tw, t + th))


def sketch_assets(av, w=640, pad=16):
    """From a cut-out avatar make (sticker, pencil_sketch), same size.
    sticker: colour avatar with a white die-cut border.
    sketch: graphite-navy line art (colour-dodge pencil + hatching + outlines) on transparency."""
    av = av.crop(av.getbbox() or (0, 0, av.width, av.height))
    av = av.resize((w, round(av.height * w / av.width)), Image.LANCZOS)
    W, H = w + 2 * pad, av.height + pad          # no border at the bottom: the body is cropped there
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0)); base.alpha_composite(av, (pad, pad))
    A = np.asarray(base.getchannel("A")).astype(np.float32) / 255
    soft = np.asarray(base.getchannel("A").filter(ImageFilter.GaussianBlur(pad * .55))).astype(np.float32)
    border = (soft > 8).astype(np.float32)
    balpha = Image.fromarray(np.clip(np.maximum(border * 255, A * 255), 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.8))
    sticker = Image.new("RGBA", (W, H), (255, 255, 255, 0)); sticker.putalpha(balpha); sticker.alpha_composite(base)
    white = Image.new("RGB", (W, H), "white"); white.paste(base, mask=base.getchannel("A"))
    g = np.asarray(white.convert("L")).astype(np.float32)
    bl = np.asarray(Image.fromarray((255 - g).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5))).astype(np.float32)
    lines = np.clip((255 - np.clip(g * 255 / (255 - bl + 1), 0, 255)) * 2.6 - 18, 0, 255)
    yy, xx = np.mgrid[0:H, 0:W]
    hatch = (((xx + yy) % 7) < 1.6) * np.clip((120 - g) / 120, 0, 1) * 150
    cross = (((xx - yy) % 9) < 1.4) * np.clip((70 - g) / 70, 0, 1) * 120
    lines = np.maximum(lines, hatch + cross)
    al = base.getchannel("A")
    lines = np.maximum(lines, np.asarray(ImageChops.subtract(al.filter(ImageFilter.MaxFilter(5)), al.filter(ImageFilter.MinFilter(3)))).astype(np.float32) * .95)
    lines = np.maximum(lines, np.asarray(ImageChops.subtract(balpha.filter(ImageFilter.MaxFilter(3)), balpha.filter(ImageFilter.MinFilter(3)))).astype(np.float32) * .35)
    lines *= np.maximum(A, border)
    sk = np.zeros((H, W, 4), np.uint8); sk[..., 0], sk[..., 1], sk[..., 2] = 34, 44, 72
    sk[..., 3] = np.clip(lines, 0, 255).astype(np.uint8)
    return sticker, Image.fromarray(sk, "RGBA")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--content", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--photo")
    ap.add_argument("--avatar")
    ap.add_argument("--card")
    ap.add_argument("--cv")
    ap.add_argument("--cutout", action="store_true")
    ap.add_argument("--url", default="")
    ap.add_argument("--og-image", default="")
    ap.add_argument("--theme", choices=["editorial", "sketch"], default="editorial")
    ap.add_argument("--template")
    a = ap.parse_args()
    if not a.template:
        name = "template-sketch.html" if a.theme == "sketch" else "template.html"
        # skill layout keeps templates in assets/, a scaffolded repo keeps them in templates/
        found = [os.path.join(HERE, "..", d, name) for d in ("assets", "templates") if os.path.exists(os.path.join(HERE, "..", d, name))]
        if not found:
            sys.exit(f"template {name} not found next to scripts/ (looked in ../assets and ../templates)")
        a.template = found[0]
    if a.theme == "sketch" and not a.avatar:
        sys.exit("--theme sketch needs --avatar (the character is the whole point of this theme)")

    content = json.load(open(a.content, encoding="utf-8"))
    tpl = open(a.template, encoding="utf-8").read()
    meta = content.get("meta", {})
    portrait = card = avatar = cv = sketch = sticker = ""
    if a.photo:
        ph = load(a.photo, a.cutout)
        if not has_alpha(ph):
            print("  warning: --photo has no transparency; the halftone will include its background. Use --cutout.")
        portrait = to_uri(fit_portrait(ph))
        card = to_uri(fit_card(ph), 80)
    if a.card:
        card = to_uri(fit_card(load(a.card, False)), 80)
    if a.avatar:
        av_img = load(a.avatar, a.cutout)
        if a.theme == "sketch":
            st, sk = sketch_assets(av_img)
            sticker, sketch = to_uri(st, 84), to_uri(sk, 80)
        else:
            avatar = to_uri(fit_avatar(av_img), 84)
    if a.cv:
        cv = base64.b64encode(open(a.cv, "rb").read()).decode()

    ttl = html.escape(meta.get("title", content.get("person", {}).get("name", "Portfolio")), quote=True)
    dsc = html.escape(meta.get("description", ""), quote=True)
    og = ['<meta property="og:type" content="website">', f'<meta property="og:title" content="{ttl}">', f'<meta property="og:description" content="{dsc}">']
    if a.url:
        og += [f'<link rel="canonical" href="{html.escape(a.url, quote=True)}">', f'<meta property="og:url" content="{html.escape(a.url, quote=True)}">']
    if a.og_image:
        og += [f'<meta property="og:image" content="{html.escape(a.og_image, quote=True)}">', '<meta property="og:image:width" content="1280">', '<meta property="og:image:height" content="640">',
               '<meta name="twitter:card" content="summary_large_image">']
    else:
        og += ['<meta name="twitter:card" content="summary">']
    data = json.dumps(content, ensure_ascii=False, indent=2).replace("</", "<\\/")
    out = (tpl.replace("{{CONTENT_JSON}}", data)
              .replace("{{TITLE}}", html.escape(meta.get("title", content.get("person", {}).get("name", "Portfolio"))))
              .replace("{{DESCRIPTION}}", html.escape(meta.get("description", ""), quote=True))
              .replace("{{PORTRAIT}}", portrait or "data:image/gif;base64,R0lGODlhAQABAAAAACw=")
              .replace("{{CARD}}", card).replace("{{AVATAR}}", avatar).replace("{{CV_B64}}", cv)
              .replace("{{OG}}", "\n".join(og)).replace("{{SKETCH}}", sketch).replace("{{STICKER}}", sticker))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write(out)
    kb = len(out.encode()) / 1024
    print(f"built {a.out} [{a.theme}] ({kb:.0f} KB) photo={'yes' if portrait else 'no'} avatar={'yes' if (avatar or sticker) else 'no'} cv={'yes' if cv else 'no'}")


if __name__ == "__main__":
    main()
