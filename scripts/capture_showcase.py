#!/usr/bin/env python3
"""Generate the README assets from the built site: animated preview, screenshots,
and the 1280x640 social-preview image.

  python scripts/capture_showcase.py                 # uses dist/
  python scripts/capture_showcase.py --out docs/img

Writes: hero.gif, social-preview.png, hero.jpg, about.jpg, skills.jpg, work.jpg, systems.jpg,
        achievements.jpg, contact.jpg, mobile-hero.jpg, mobile-work.jpg  (+ editorial-*.jpg if dist/editorial exists)
Needs: pip install playwright pillow && playwright install chromium, and ffmpeg on PATH (for the GIF).
"""
import argparse, asyncio, os, shutil, subprocess, tempfile
from PIL import Image
from playwright.async_api import async_playwright

GL = ["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"]


def jpg(src, dst, width=None, q=86):
    im = Image.open(src).convert("RGB")
    if width and im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    im.save(dst, "JPEG", quality=q, optimize=True, progressive=True)


async def sweep(page, box, passes=3):
    """Move the mouse in a loose zig-zag across a bounding box, in real time (so the video shows it)."""
    x0, y0, w, h = box["x"], box["y"], box["width"], box["height"]
    pts = []
    for p in range(passes):
        y = y0 + h * (0.2 + 0.6 * p / max(1, passes - 1))
        pts += [(x0 + w * 0.12, y), (x0 + w * 0.88, y + h * 0.06)]
    await page.mouse.move(*pts[0])
    for (x, y) in pts[1:]:
        await page.mouse.move(x, y, steps=1)  # position first, then glide
        await page.wait_for_timeout(1)
    for (x, y), (nx, ny) in zip(pts, pts[1:]):
        for i in range(1, 31):
            await page.mouse.move(x + (nx - x) * i / 30, y + (ny - y) * i / 30)
            await page.wait_for_timeout(16)


async def run(dist, out):
    os.makedirs(out, exist_ok=True)
    sketch = os.path.join(dist, "index.html")
    editorial = os.path.join(dist, "editorial", "index.html")
    tmp = tempfile.mkdtemp()
    async with async_playwright() as p:
        b = await p.chromium.launch(args=GL)

        # ---- animated preview (video -> GIF) ----
        ctx = await b.new_context(viewport={"width": 1280, "height": 720}, record_video_dir=tmp, record_video_size={"width": 1280, "height": 720})
        pg = await ctx.new_page()
        await pg.goto("file://" + os.path.abspath(sketch))
        await pg.wait_for_timeout(4200)
        host = await pg.query_selector("#skChar") or await pg.query_selector("#top")
        box = await host.bounding_box()
        await sweep(pg, box, passes=2)
        await pg.wait_for_timeout(1800)
        await ctx.close()
        webm = [os.path.join(tmp, f) for f in os.listdir(tmp) if f.endswith(".webm")][0]
        if shutil.which("ffmpeg"):
            vf = "fps=10,scale=800:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "0.6", "-i", webm, "-vf", vf, "-loop", "0", os.path.join(out, "hero.gif")], check=True)
        else:
            print("ffmpeg not found: skipped hero.gif")

        # ---- social preview (1280x640) ----
        pg = await b.new_page(viewport={"width": 1280, "height": 640})
        await pg.goto("file://" + os.path.abspath(sketch))
        await pg.wait_for_timeout(4200)
        sp = os.path.join(tmp, "sp.png")
        await pg.screenshot(path=sp)
        im = Image.open(sp).convert("RGB")
        im.save(os.path.join(out, "social-preview.png"), optimize=True)
        if os.path.getsize(os.path.join(out, "social-preview.png")) > 950_000:
            im.quantize(256).convert("RGB").save(os.path.join(out, "social-preview.png"), optimize=True)

        # ---- desktop + mobile screenshots ----
        async def shots(path, prefix, sections):
            d = await b.new_page(viewport={"width": 1440, "height": 900})
            await d.goto("file://" + os.path.abspath(path))
            await d.wait_for_timeout(4200)
            f = os.path.join(tmp, "x.png")
            await d.screenshot(path=f); jpg(f, os.path.join(out, f"{prefix}hero.jpg"), 1440)
            for sid in sections:
                if not await d.evaluate(f"!!document.getElementById('{sid}')"):
                    continue
                if sid == "achievements":
                    await d.evaluate("var e=document.getElementById('proudPin');if(e)window.scrollTo(0,e.getBoundingClientRect().top+scrollY+(e.offsetHeight-innerHeight)*.45)")
                else:
                    await d.evaluate(f"document.getElementById('{sid}').scrollIntoView()")
                await d.wait_for_timeout(2800)
                await d.screenshot(path=f); jpg(f, os.path.join(out, f"{prefix}{sid}.jpg"), 1440)
            await d.close()
        await shots(sketch, "", ["about", "skills", "work", "systems", "achievements", "contact"])

        m = await b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2)
        await m.goto("file://" + os.path.abspath(sketch))
        await m.wait_for_timeout(4200)
        f = os.path.join(tmp, "m.png")
        await m.screenshot(path=f); jpg(f, os.path.join(out, "mobile-hero.jpg"), 780)
        await m.evaluate("document.getElementById('work').scrollIntoView()")
        await m.wait_for_timeout(1800)
        await m.screenshot(path=f); jpg(f, os.path.join(out, "mobile-work.jpg"), 780)

        # ---- editorial theme (optional) ----
        if os.path.exists(editorial):
            e = await b.new_page(viewport={"width": 1440, "height": 900})
            await e.goto("file://" + os.path.abspath(editorial))
            await e.wait_for_timeout(3200)
            f = os.path.join(tmp, "e.png")
            await e.screenshot(path=f); jpg(f, os.path.join(out, "editorial-hero.jpg"), 1440)
            await e.mouse.move(180, 240)
            for x, y in [(520, 330), (860, 230), (1180, 330), (1300, 520), (900, 600), (480, 560), (260, 420)]:
                await e.mouse.move(x, y, steps=14)
            await e.wait_for_timeout(80)
            await e.screenshot(path=f); jpg(f, os.path.join(out, "editorial-reveal.jpg"), 1440)
        await b.close()
    shutil.rmtree(tmp, ignore_errors=True)
    for n in sorted(os.listdir(out)):
        print(f"{os.path.getsize(os.path.join(out, n)) / 1024:7.0f} KB  {n}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dist", default="dist")
    ap.add_argument("--out", default="docs/img")
    a = ap.parse_args()
    asyncio.run(run(a.dist, a.out))
