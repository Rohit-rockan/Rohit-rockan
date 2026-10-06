"""
Generate the animated profile hero banners in assets/hero/.

    python scripts/gen_hero.py

Builds an ASCII portrait from scripts/avatar.png and wraps it in a terminal-style
card with a profile panel. Writes four SVGs: desktop/mobile x dark/light.
Edit PROFILE / WORK below to change the text.
"""
from html import escape
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "hero"

PROFILE = [
    ("Name", "Rohit Awasthi"),
    ("Role", "AI & full-stack builder"),
    ("Edu", "student @ NIT Jalandhar"),
    ("Focus", "LLM apps · RAG · long-context memory"),
    ("Also", "streaming platforms · applied ML"),
    ("Stack", "Python · TypeScript · Node.js · SQLite"),
]
WORK = [
    ("writingdao", "context compiler + memory OS for AI writing"),
    ("novel-rag", "hybrid BM25 + dense retrieval over fiction"),
    ("nompyr", "anime discovery & streaming platform"),
    ("hydraulic_conductivity", "ANN / RF / SVM / fuzzy soil models"),
]

THEMES = {
    "dark": dict(
        bg0="#0D1117", bg1="#161B22", panel="#161B22", text="#E6EDF3", muted="#8B949E",
        accent="#58A6FF", accent2="#D2A8FF", ok="#3FB950", ascii0="#F0F6FC", ascii1="#79C0FF",
        line="#30363D",
    ),
    "light": dict(
        bg0="#FFFFFF", bg1="#F6F8FA", panel="#F6F8FA", text="#1F2328", muted="#59636E",
        accent="#0969DA", accent2="#8250DF", ok="#1A7F37", ascii0="#1F2328", ascii1="#0969DA",
        line="#D0D7DE",
    ),
}

RAMP = " .:-=+*#%@"


def ascii_portrait(cols: int, rows: int) -> list[str]:
    im = Image.open(Path(__file__).with_name("avatar.png")).convert("L")
    im = ImageOps.autocontrast(im.crop((40, 0, 420, 400)), cutoff=3)
    edges = im.filter(ImageFilter.GaussianBlur(1)).filter(ImageFilter.FIND_EDGES)
    edges = ImageOps.crop(edges, 3)  # FIND_EDGES lights up the image border
    im, edges = im.resize((cols, rows)), edges.resize((cols, rows), Image.BOX)
    px, ex = im.load(), edges.load()
    lines = []
    for y in range(rows):
        row = []
        for x in range(cols):
            # fade the square corners so the portrait reads as a circle
            dx, dy = (x - cols / 2) / (cols / 2), (y - rows / 2) / (rows / 2)
            fade = max(0.0, min(1.0, (1.1 - (dx * dx + dy * dy) ** 0.5) * 5))
            dark = ((255 - px[x, y]) / 255) ** 1.8
            ink = max(dark * 0.8, min(1.0, ex[x, y] / 40) * 0.9) * fade
            row.append(RAMP[min(len(RAMP) - 1, int(ink * len(RAMP)))])
        lines.append("".join(row).rstrip())
    return lines


def style(t: dict) -> str:
    return f"""
  <style>
    text, tspan {{ white-space: pre; font-family: 'Courier New', Consolas, monospace; }}
    .ascii {{ font-size: 6.6px; letter-spacing: -0.2px; fill: url(#ascii-grad); }}
    .label {{ font-size: 11px; letter-spacing: 2px; fill: {t['muted']}; }}
    .term {{ font-size: 12px; fill: {t['muted']}; }}
    .live {{ font-size: 10px; letter-spacing: 1px; fill: {t['ok']}; font-weight: 700; }}
    .prompt {{ font-size: 15px; fill: {t['accent']}; font-weight: 700; }}
    .head {{ font-size: 22px; fill: {t['text']}; font-weight: 700; }}
    .key {{ font-size: 14px; fill: {t['accent']}; font-weight: 700; }}
    .val {{ font-size: 14px; fill: {t['text']}; }}
    .sec {{ font-size: 12px; letter-spacing: 2px; fill: {t['accent2']}; font-weight: 700; }}
    .repo {{ font-size: 14px; fill: {t['accent2']}; font-weight: 700; }}
    .desc {{ font-size: 13px; fill: {t['muted']}; }}
    .orbit {{ transform-box: view-box; }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
    @keyframes spin-back {{ to {{ transform: rotate(-360deg); }} }}
    @keyframes sweep {{ from {{ transform: translateY(-60px); }} to {{ transform: translateY(700px); }} }}
    @keyframes blink {{ 0%, 49% {{ opacity: 1; }} 50%, 100% {{ opacity: 0; }} }}
    @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.25; }} }}
    @keyframes reveal {{ from {{ opacity: 0; transform: translateX(-8px); }} to {{ opacity: 1; transform: none; }} }}
    @media (prefers-reduced-motion: no-preference) {{
      .spin {{ animation: spin 40s linear infinite; }}
      .spin-back {{ animation: spin-back 30s linear infinite; }}
      .sweep {{ animation: sweep 7s linear infinite; }}
      .cursor {{ animation: blink 1.1s step-end infinite; }}
      .pulse {{ animation: pulse 2s ease-in-out infinite; }}
      .line {{ animation: reveal 0.5s ease-out both; }}
    }}
    @media (prefers-reduced-motion: reduce) {{ .sweep {{ display: none; }} }}
  </style>"""


def defs(t: dict, clip: tuple) -> str:
    x, y, w, h = clip
    return f"""
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t['bg0']}"/><stop offset="1" stop-color="{t['bg1']}"/></linearGradient>
  <linearGradient id="ascii-grad" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t['ascii0']}"/><stop offset="1" stop-color="{t['ascii1']}"/></linearGradient>
  <linearGradient id="border" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t['line']}"/><stop offset="0.5" stop-color="{t['accent']}"/><stop offset="1" stop-color="{t['line']}"/></linearGradient>
  <linearGradient id="scan" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t['accent']}" stop-opacity="0"/><stop offset="0.5" stop-color="{t['accent']}" stop-opacity="0.35"/><stop offset="1" stop-color="{t['accent']}" stop-opacity="0"/></linearGradient>
  <radialGradient id="halo"><stop offset="0" stop-color="{t['accent']}" stop-opacity="0.14"/><stop offset="1" stop-color="{t['accent']}" stop-opacity="0"/></radialGradient>
  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M 40 0 H 0 V 40" fill="none" stroke="{t['muted']}" stroke-width="0.6" opacity="0.12"/></pattern>
  <pattern id="scanlines" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="{t['accent']}" opacity="0.04"/></pattern>
  <clipPath id="pclip"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12"/></clipPath>
</defs>"""


def chrome(t: dict, width: int, height: int) -> str:
    return f"""
<rect width="{width}" height="{height}" rx="18" fill="url(#bg)"/>
<rect width="{width}" height="{height}" rx="18" fill="url(#scanlines)"/>
<rect x="3" y="3" width="{width - 6}" height="34" rx="16" fill="{t['panel']}" fill-opacity="0.9"/>
<circle cx="24" cy="20" r="5" fill="#FF5F57"/><circle cx="42" cy="20" r="5" fill="#FEBC2E"/><circle cx="60" cy="20" r="5" fill="#28C840"/>
<text x="{width / 2}" y="25" text-anchor="middle" class="term">rohit@build ~ % ./profile</text>
<circle class="pulse" cx="{width - 92}" cy="20" r="4" fill="{t['ok']}"/><text x="{width - 82}" y="24" class="live">BUILDING</text>"""


def portrait(t: dict, box: tuple, cols: int, rows: int, line_h: float, char_w: float) -> str:
    x, y, w, h = box
    cx, cy = x + w / 2, y + h / 2
    art = ascii_portrait(cols, rows)
    ox = x + (w - cols * char_w) / 2
    oy = y + (h - rows * line_h) / 2 + line_h
    spans = "\n".join(
        f'<tspan x="{ox:.1f}" y="{oy + i * line_h:.2f}">{escape(line)}</tspan>'
        for i, line in enumerate(art) if line
    )
    return f"""
<g clip-path="url(#pclip)" aria-hidden="true">
  <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#grid)"/>
  <ellipse cx="{cx}" cy="{cy}" rx="{w * 0.48}" ry="{h * 0.44}" fill="url(#halo)"/>
  <ellipse class="orbit spin" style="transform-origin:{cx}px {cy}px" cx="{cx}" cy="{cy}" rx="{w * 0.46}" ry="{h * 0.30}" fill="none" stroke="{t['accent']}" stroke-dasharray="3 14" opacity="0.35"/>
  <ellipse class="orbit spin-back" style="transform-origin:{cx}px {cy}px" cx="{cx}" cy="{cy}" rx="{w * 0.36}" ry="{h * 0.22}" fill="none" stroke="{t['accent2']}" stroke-dasharray="26 22" opacity="0.25"/>
  <text class="ascii">{spans}</text>
  <rect class="sweep" x="{x}" y="{y}" width="{w}" height="60" fill="url(#scan)"/>
</g>"""


def info(t: dict, x: float, y: float, row_h: float, wrap_work: bool) -> tuple[str, float]:
    out, i = [], 0

    def line(body: str, dy: float):
        nonlocal y, i
        y += dy
        out.append(f'<g class="line" style="animation-delay:{0.15 + i * 0.12:.2f}s"><text x="{x}" y="{y:.1f}">{body}</text></g>')
        i += 1

    line('<tspan class="prompt">$ whoami</tspan>', 0)
    line('<tspan class="head">Rohit Awasthi</tspan>', row_h * 1.6)
    y += 12
    out.append(f'<line x1="{x}" y1="{y:.1f}" x2="{x + 560}" y2="{y:.1f}" stroke="{t["line"]}"/>')
    for key, val in PROFILE[1:]:
        line(f'<tspan class="key">{key:<6}</tspan><tspan class="val"> {escape(val)}</tspan>', row_h)
    y += 10
    line('<tspan class="sec">SELECTED WORK</tspan>', row_h * 1.4)
    for name, desc in WORK:
        if wrap_work:
            line(f'<tspan class="repo">▸ {escape(name)}</tspan>', row_h)
            line(f'<tspan class="desc">  {escape(desc)}</tspan>', row_h * 0.9)
        else:
            line(f'<tspan class="repo">▸ {escape(name):<23}</tspan><tspan class="desc">{escape(desc)}</tspan>', row_h)
    line(f'<tspan class="prompt">$ </tspan><tspan class="cursor" fill="{t["accent"]}">█</tspan>', row_h * 1.5)
    swatch_y = y + 22
    for k, c in enumerate(["#FF7B72", "#FFA657", "#E3B341", "#3FB950", "#58A6FF", "#D2A8FF", t["muted"]]):
        out.append(f'<rect x="{x + k * 26}" y="{swatch_y:.1f}" width="22" height="10" rx="2" fill="{c}"/>')
    return "\n".join(out), swatch_y + 10


def desktop(theme: str) -> str:
    t, W, H = THEMES[theme], 1180, 560
    pbox = (24, 72, 440, 456)
    body, _ = info(t, 520, 112, 27, wrap_work=False)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title">
<title id="title">Rohit Awasthi — AI &amp; full-stack builder</title>
{defs(t, pbox)}{style(t)}{chrome(t, W, H)}
<rect x="14" y="62" width="460" height="476" rx="14" fill="{t['panel']}" fill-opacity="0.35" stroke="url(#border)" stroke-opacity="0.5"/>
<rect x="490" y="62" width="672" height="476" rx="14" fill="{t['panel']}" fill-opacity="0.4" stroke="url(#border)" stroke-opacity="0.5"/>
<text x="30" y="56" class="label">PORTRAIT / ROHIT</text><text x="506" y="56" class="label">PROFILE / BUILDER</text>
{portrait(t, pbox, 112, 66, 6.8, 3.75)}
{body}
</svg>
"""


def mobile(theme: str) -> str:
    t, W = THEMES[theme], 640
    pbox = (24, 72, 592, 400)
    body, bottom = info(t, 40, 530, 26, wrap_work=True)
    H = int(bottom + 40)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title">
<title id="title">Rohit Awasthi — AI &amp; full-stack builder</title>
{defs(t, pbox)}{style(t)}{chrome(t, W, H)}
<rect x="14" y="62" width="612" height="420" rx="14" fill="{t['panel']}" fill-opacity="0.35" stroke="url(#border)" stroke-opacity="0.5"/>
<rect x="14" y="496" width="612" height="{H - 510}" rx="14" fill="{t['panel']}" fill-opacity="0.4" stroke="url(#border)" stroke-opacity="0.5"/>
{portrait(t, pbox, 110, 58, 6.8, 3.75)}
{body}
</svg>
"""


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        (OUT / f"hero-{theme}.svg").write_text(desktop(theme), encoding="utf-8")
        (OUT / f"hero-mobile-{theme}.svg").write_text(mobile(theme), encoding="utf-8")
    print("wrote", *sorted(p.name for p in OUT.glob("*.svg")))
