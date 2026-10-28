"""Regenerate docs/screenshots/*.png from webapp/index.html (needs Playwright + Chromium).

Math.random is replaced by a seeded generator so the screenshots are reproducible.
"""
import asyncio, os, sys
from playwright.async_api import async_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "docs", "screenshots")
SEED = """(() => { let a = %d; Math.random = function () { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; })();"""

RESTART_AT_DAY0 = """(sp) => { const a = window.__ag; a.state.playing = false; document.getElementById('restart').click(); a.state.speed = sp; a.state.playing = true; }"""
PAUSE_AT = """(target) => new Promise((res) => { const f = () => { const w = window.__ag.world(); if (w.t >= target) { window.__ag.state.playing = false; res(w.t); } else requestAnimationFrame(f); }; f(); })"""

SCENES = [  # (file, hash preset, seed, target day, speed index)
    ("01-early-random-creatures.png", "natural", 7, 60, 0),
    ("02-hand-coded-expert.png", "expert", 7, 2500, 2),
    ("03-survival-only-evolved.png", "natural", 7, 30000, 3),
    ("04-random-parents-control.png", "drift", 7, 30000, 3),
]

async def main():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for fname, preset, seed, day, speed in SCENES:
            ctx = await b.new_context(viewport={"width": 1280, "height": 1000}, device_scale_factor=1.4)
            pg = await ctx.new_page()
            await pg.add_init_script(SEED % seed)
            await pg.route("**/fonts.*/**", lambda r: r.abort())   # offline-friendly: fall back to system fonts
            await pg.goto("file://" + os.path.join(ROOT, "webapp", "index.html") + "#" + preset, wait_until="domcontentloaded")
            await pg.evaluate(RESTART_AT_DAY0, speed)
            await pg.evaluate(PAUSE_AT, day)   # the page pauses itself on the first frame at or after `day`
            await pg.wait_for_timeout(700)
            stage = await pg.query_selector("section.stage")
            await stage.screenshot(path=os.path.join(OUT, fname))
            print("wrote", fname, await pg.evaluate("window.__ag.world().t"), "|", await pg.evaluate("document.getElementById('headline').textContent"))
            await ctx.close()
        ctx = await b.new_context(viewport={"width": 400, "height": 860}, device_scale_factor=2, is_mobile=True)
        pg = await ctx.new_page()
        await pg.add_init_script(SEED % 7)
        await pg.route("**/fonts.*/**", lambda r: r.abort())
        await pg.goto("file://" + os.path.join(ROOT, "webapp", "index.html") + "#expert", wait_until="domcontentloaded")
        await pg.evaluate(RESTART_AT_DAY0, 2)
        await pg.evaluate(PAUSE_AT, 2500)
        await pg.wait_for_timeout(500)
        await pg.screenshot(path=os.path.join(OUT, "05-phone.png"))
        print("wrote 05-phone.png")
        await b.close()

asyncio.run(main())
