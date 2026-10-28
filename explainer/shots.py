import asyncio, sys
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/ex"
async def main():
    import os; os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for name, vw, vh in (("desktop", 1280, 900), ("phone", 400, 860)):
            pg = await b.new_page(viewport={"width": vw, "height": vh})
            errs = []
            pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            pg.on("pageerror", lambda e: errs.append(str(e)))
            await pg.route("**/fonts.*/**", lambda r: r.abort())
            await pg.goto("file:///home/claude/agency-from-gradients/explainer/index.html", wait_until="domcontentloaded")
            await pg.wait_for_timeout(2500)
            await pg.evaluate("document.getElementById('catch').value=60; document.getElementById('catch').dispatchEvent(new Event('input'))")
            await pg.wait_for_timeout(3500)
            await pg.screenshot(path=f"{OUT}/{name}-top.png")
            await pg.evaluate("window.__pond.state.playing=false; window.__pond.step(4000)")
            await pg.evaluate("document.getElementById('pondsec').scrollIntoView()")
            await pg.wait_for_timeout(500)
            await pg.screenshot(path=f"{OUT}/{name}-pond.png")
            await pg.evaluate("document.getElementById('results').scrollIntoView(); window.scrollBy(0,700)")
            await pg.wait_for_timeout(300)
            await pg.screenshot(path=f"{OUT}/{name}-results.png")
            await pg.screenshot(path=f"{OUT}/{name}-full.png", full_page=True)
            ow = await pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            print(name, "errors:", errs[:3], "h-overflow:", ow)
        await b.close()
asyncio.run(main())
