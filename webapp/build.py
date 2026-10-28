"""Build webapp/index.html (standalone page) and webapp/dist/artifact.html (fragment for publishing)."""
import pathlib, re
root = pathlib.Path(__file__).parent
tpl = (root / "src" / "template.html").read_text()
sim = (root / "sim.js").read_text()
app = (root / "src" / "app.js").read_text()
frag = tpl.replace("{{SIM}}", sim.replace("</script>", "<\\/script>")).replace("{{APP}}", app.replace("</script>", "<\\/script>"))
(root / "dist").mkdir(exist_ok=True)
(root / "dist" / "artifact.html").write_text(frag)
title = re.search(r"<title>.*?</title>", frag, re.S).group(0)
body = frag.replace(title, "", 1)
full = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1,viewport-fit=cover\">"
        + title +
        "<style>:root{color-scheme:dark;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}"
        "[hidden]{display:none!important}</style></head><body>" + body + "</body></html>\n")
(root / "index.html").write_text(full)
print("built", len(full) // 1024, "KB")
