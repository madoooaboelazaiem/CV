#!/usr/bin/env python3
"""Screenshot QA for a built site: desktop + mobile, every section, a simulated
scratch reveal, JS errors and horizontal overflow.

Usage: python qa.py index.html outdir/
Needs: playwright with chromium (pip install playwright && playwright install chromium)
"""
import asyncio, json, os, sys
from playwright.async_api import async_playwright

SECTIONS = ["about", "ai", "skills", "work", "systems", "experience", "learning", "achievements", "contact"]

async def run(path, out):
    os.makedirs(out, exist_ok=True)
    url = "file://" + os.path.abspath(path)
    report = {"errors": [], "overflow": {}, "shots": []}
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for name, vp in [("desktop", {"width": 1440, "height": 900}), ("mobile", {"width": 390, "height": 844})]:
            pg = await b.new_page(viewport=vp)
            pg.on("pageerror", lambda e: report["errors"].append(str(e)))
            await pg.goto(url)
            await pg.wait_for_timeout(2600)
            f = f"{out}/{name}-hero.png"; await pg.screenshot(path=f); report["shots"].append(f)
            pts = [(vp["width"] * x, vp["height"] * y) for x, y in [(.1, .35), (.35, .45), (.6, .4), (.8, .3), (.9, .5), (.6, .7)]]
            await pg.mouse.move(*pts[0])
            for x, y in pts[1:]:
                await pg.mouse.move(x, y, steps=12)
            await pg.wait_for_timeout(150)
            f = f"{out}/{name}-reveal.png"; await pg.screenshot(path=f); report["shots"].append(f)
            for sid in SECTIONS:
                if not await pg.evaluate(f"!!document.getElementById('{sid}')"):
                    continue
                await pg.evaluate(f"document.getElementById('{sid}').scrollIntoView()")
                await pg.wait_for_timeout(1400)
                f = f"{out}/{name}-{sid}.png"; await pg.screenshot(path=f); report["shots"].append(f)
            report["overflow"][name] = await pg.evaluate("document.documentElement.scrollWidth - innerWidth")
        await b.close()
    json.dump(report, open(f"{out}/report.json", "w"), indent=2)
    print(json.dumps({"errors": report["errors"], "overflow_px": report["overflow"], "shots": len(report["shots"])}, indent=2))

if __name__ == "__main__":
    asyncio.run(run(sys.argv[1], sys.argv[2]))
