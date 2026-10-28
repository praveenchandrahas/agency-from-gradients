"""Build explainer/index.html from src/ and the shared engine webapp/sim.js."""
import pathlib
root = pathlib.Path(__file__).parent
tpl = (root / "src" / "template.html").read_text()
sim = (root.parent / "webapp" / "sim.js").read_text()
app = (root / "src" / "app.js").read_text()
body = tpl.replace("{{SIM}}", sim.replace("</script>", "<\\/script>")).replace("{{APP}}", app.replace("</script>", "<\\/script>"))
import re
title = re.search(r"<title>.*?</title>", body, re.S).group(0)
desc = re.search(r"<meta name=\"description\".*?>", body, re.S).group(0)
body = body.replace(title, "", 1).replace(desc, "", 1)
full = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1,viewport-fit=cover\">"
        + title + desc + "</head><body>" + body + "</body></html>\n")
(root / "index.html").write_text(full)
print("built", len(full) // 1024, "KB")
