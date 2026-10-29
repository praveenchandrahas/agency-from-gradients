"""Build learn/index.html and learn/film.html (full documents, fonts inlined) and learn/artifact/* (fragments)."""
import base64, pathlib
HERE = pathlib.Path(__file__).parent
import os
# fonts come from: npm i @fontsource-variable/bricolage-grotesque @fontsource-variable/source-serif-4 @fontsource/jetbrains-mono
FONTS = pathlib.Path(os.environ.get("FONTS_DIR", "/tmp/fonts/node_modules"))
FACES = [
    ("Bricolage Grotesque Variable", "100% 100%", "200 800", "@fontsource-variable/bricolage-grotesque/files/bricolage-grotesque-latin-wght-normal.woff2"),
    ("Source Serif 4 Variable", "100% 100%", "200 900", "@fontsource-variable/source-serif-4/files/source-serif-4-latin-wght-normal.woff2"),
    ("JetBrains Mono", "100% 100%", "400", "@fontsource/jetbrains-mono/files/jetbrains-mono-latin-400-normal.woff2"),
    ("JetBrains Mono", "100% 100%", "500", "@fontsource/jetbrains-mono/files/jetbrains-mono-latin-500-normal.woff2"),
]
def faces():
    out = []
    for fam, stretch, weight, rel in FACES:
        b = base64.b64encode((FONTS / rel).read_bytes()).decode()
        out.append(f'@font-face{{font-family:"{fam}";font-weight:{weight};font-style:normal;font-display:swap;src:url(data:font/woff2;base64,{b}) format("woff2")}}')
    return "\n".join(out)
PREFIX = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>:root{color-scheme:light}html,body{margin:0}</style>\n'
for name, out in (("video", "film"), ("site", "index")):
    src = HERE / "src" / f"{name}.src.html"
    if not src.exists():
        continue
    frag = src.read_text().replace("/*FONTFACES*/", faces())
    (HERE / "artifact").mkdir(exist_ok=True)
    (HERE / "artifact" / f"{out}.html").write_text(frag)
    (HERE / f"{out}.html").write_text(PREFIX + frag)
    print(out, len(frag) // 1024, "KB")
