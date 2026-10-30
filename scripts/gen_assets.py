#!/usr/bin/env python3
"""Generate the pixel neon README assets (headers, bio terminal, badges, project cards).
Run: python3 scripts/gen_assets.py  (fetches live star counts from the GitHub API)."""
import json, os, urllib.request
from xml.sax.saxutils import escape as esc
OUT = os.path.join(os.path.dirname(__file__), "..", "assets")
USER = "Devil1716"
BG, BG2, PINK, CYAN, GREEN, TXT, DIM = "#1a1033", "#120a24", "#ff4fd8", "#3ef3ff", "#39d353", "#e9e4ff", "#9a8cc8"
FONT = "'JetBrains Mono','Fira Code',Consolas,'Courier New',monospace"
LANG = {"Kotlin": "#a97bff", "JavaScript": "#f1e05a", "Dart": "#00b4ab", "Python": "#3572A5",
        "TypeScript": "#3178c6", "Java": "#b07219"}
PROJECTS = [
    ("agent-phone-app", "On-device Gemma agent for normal Android phones."),
    ("drapesense", "Fabric scanner that turns a camera swatch into drape, yardage and a cutting diagram."),
    ("bluetooth-manet-android", "Bluetooth MANET demo with RFCOMM relay and TTL forwarding."),
    ("kosh", "Offline pocket ledger for daily income and spending."),
    ("isro-bah-challenge9-shwfs", "Shack Hartmann wavefront reconstruction, ISRO BAH Challenge 9."),
    ("AgentIDE", "Agent workspace experiment."),
]
GLOW = """<filter id="g" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>"""

def w(name, s):
    open(os.path.join(OUT, name), "w").write(s)

def pixel_frame(W, H, color, t=2):
    # stepped pixel corners: 2px border with notched corners
    return (f'<rect x="{t*2}" y="0" width="{W-t*4}" height="{t}" fill="{color}"/>'
            f'<rect x="{t*2}" y="{H-t}" width="{W-t*4}" height="{t}" fill="{color}"/>'
            f'<rect x="0" y="{t*2}" width="{t}" height="{H-t*4}" fill="{color}"/>'
            f'<rect x="{W-t}" y="{t*2}" width="{t}" height="{H-t*4}" fill="{color}"/>'
            f'<rect x="{t}" y="{t}" width="{t}" height="{t}" fill="{color}"/>'
            f'<rect x="{W-t*2}" y="{t}" width="{t}" height="{t}" fill="{color}"/>'
            f'<rect x="{t}" y="{H-t*2}" width="{t}" height="{t}" fill="{color}"/>'
            f'<rect x="{W-t*2}" y="{H-t*2}" width="{t}" height="{t}" fill="{color}"/>')

def header(fname, label):
    W, H = 420, 48
    tw = len(label) * 13.2 + 26
    x0 = (W - tw) / 2
    s = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{label}">
<defs>{GLOW}<style>.c{{animation:b 1s steps(1) infinite}}@keyframes b{{50%{{opacity:0}}}}</style></defs>
<rect x="4" y="4" width="{W-8}" height="{H-8}" fill="{BG2}"/>
{pixel_frame(W, H, CYAN)}
<g fill="{PINK}">{''.join(f'<rect x="{12+i*8}" y="22" width="4" height="4"/>' for i in range(3))}{''.join(f'<rect x="{W-16-i*8}" y="22" width="4" height="4"/>' for i in range(3))}</g>
<g filter="url(#g)" font-family="{FONT}" font-size="22" font-weight="700">
<text x="{x0}" y="31" fill="{PINK}">&gt;</text><text x="{x0+20}" y="31" fill="{CYAN}">{label}</text>
<rect class="c" x="{x0+22+len(label)*13.2+4}" y="14" width="11" height="20" fill="{GREEN}"/></g>
</svg>'''
    w(fname, s)

def bio():
    lines = [("$ whoami", PINK), ("B.Tech AI/ML @ Amity University Bengaluru (May 2027)", TXT),
             ("Technical Lead at Quickoo", TXT), ("Building on-device agents, Android, FastAPI backends", TXT),
             ("Open to remote Backend / Agentic AI internships", GREEN)]
    W, H = 640, 214
    rows = []
    for i, (t, c) in enumerate(lines):
        y = 74 + i * 28
        n = len(t) * 9.65 + 4
        d0, d1 = 0.3 + i * 0.7, 0.7
        pre = "" if i == 0 else '<tspan fill="#3ef3ff">&gt; </tspan>'
        rows.append(f'<clipPath id="k{i}"><rect x="24" y="{y-18}" height="26" width="0"><animate attributeName="width" from="0" to="{n+24}" begin="{d0}s" dur="{d1}s" fill="freeze" calcMode="discrete" keyTimes="{";".join(str(k/12) for k in range(13))}" values="{";".join(str(round((n+24)*k/12)) for k in range(13))}"/></rect></clipPath>'
                    f'<text clip-path="url(#k{i})" x="24" y="{y}" fill="{c}" font-family="{FONT}" font-size="16">{pre}{esc(t)}</text>')
    s = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="About Sharan: {esc(' | '.join(l for l,_ in lines[1:]))}">
<defs>{GLOW}<style>.c{{animation:b 1s steps(1) infinite}}@keyframes b{{50%{{opacity:0}}}}</style></defs>
<rect x="4" y="4" width="{W-8}" height="{H-8}" fill="{BG}"/>
<rect x="4" y="4" width="{W-8}" height="30" fill="#2a1850"/>
{pixel_frame(W, H, PINK)}<rect x="4" y="34" width="{W-8}" height="2" fill="{PINK}"/>
<rect x="16" y="14" width="10" height="10" fill="#ff5f57"/><rect x="32" y="14" width="10" height="10" fill="#febc2e"/><rect x="48" y="14" width="10" height="10" fill="#28c840"/>
<text x="{W/2}" y="24" text-anchor="middle" fill="{DIM}" font-family="{FONT}" font-size="13">sharan@devil1716: ~/about_me</text>
{''.join(rows)}
<rect class="c" x="24" y="{74+5*28-16}" width="10" height="18" fill="{GREEN}" filter="url(#g)"/>
</svg>'''
    w("bio-terminal.svg", s)

def badge(fname, label, color):
    W, H = 150, 40
    s = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{label}">
<defs>{GLOW}</defs><rect x="4" y="4" width="{W-8}" height="{H-8}" fill="{BG}"/>{pixel_frame(W, H, color)}
<rect x="14" y="16" width="8" height="8" fill="{color}" filter="url(#g)"/>
<text x="{W/2+8}" y="26" text-anchor="middle" fill="{color}" filter="url(#g)" font-family="{FONT}" font-size="15" font-weight="700" letter-spacing="2">{label}</text></svg>'''
    w(fname, s)

def wrap(t, n=52):
    out, cur = [], ""
    for word in t.split():
        if len(cur) + len(word) + 1 > n and cur:
            out.append(cur); cur = word
        else:
            cur = (cur + " " + word).strip()
    return out + [cur]

def repo(name):
    try:
        r = urllib.request.Request(f"https://api.github.com/repos/{USER}/{name}", headers={"User-Agent": "gen"})
        if os.environ.get("GITHUB_TOKEN"): r.add_header("Authorization", "Bearer " + os.environ["GITHUB_TOKEN"])
        d = json.load(urllib.request.urlopen(r, timeout=15))
        return d.get("language") or "Code", d.get("stargazers_count", 0), d.get("forks_count", 0)
    except Exception:
        return "Code", 0, 0

def card(name, desc):
    lang, stars, forks = repo(name)
    col = LANG.get(lang, CYAN)
    W, H = 500, 140
    d = "".join(f'<text x="22" y="{74+i*20}" fill="{TXT}" font-family="{FONT}" font-size="14.5">{esc(l)}</text>' for i, l in enumerate(wrap(desc)[:2]))
    star = "".join(f'<rect x="{x}" y="{y}" width="2" height="2"/>' for x, y in [(4,0),(2,2),(4,2),(6,2),(0,4),(2,4),(4,4),(6,4),(8,4),(2,6),(4,6),(6,6),(0,8),(2,8),(6,8),(8,8)])
    s = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{name}: {esc(desc)}">
<defs>{GLOW}<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG}"/><stop offset="1" stop-color="{BG2}"/></linearGradient></defs>
<rect x="4" y="4" width="{W-8}" height="{H-8}" fill="url(#bg)"/>{pixel_frame(W, H, col)}
<rect x="4" y="4" width="6" height="{H-8}" fill="{col}" opacity="0.35"/>
<g filter="url(#g)"><rect x="22" y="22" width="12" height="12" fill="none" stroke="{col}" stroke-width="2"/><rect x="26" y="26" width="4" height="4" fill="{col}"/>
<text x="44" y="34" fill="{CYAN}" font-family="{FONT}" font-size="18" font-weight="700">{esc(name)}</text></g>
<rect x="22" y="46" width="{W-44}" height="2" fill="{col}" opacity="0.25"/>
{d}
<rect x="22" y="112" width="10" height="10" fill="{col}"/><text x="40" y="121" fill="{DIM}" font-family="{FONT}" font-size="12.5">{esc(lang)}</text>
<g fill="{GREEN}" transform="translate({W-92},112)">{star}</g><text x="{W-76}" y="121" fill="{DIM}" font-family="{FONT}" font-size="12.5">{stars} stars</text>
<text x="{W-170}" y="121" fill="{DIM}" font-family="{FONT}" font-size="12.5">{forks} forks</text>
</svg>'''
    w(f"cards/{name}.svg", s)

if __name__ == "__main__":
    os.makedirs(os.path.join(OUT, "cards"), exist_ok=True)
    for f, l in [("header-about.svg", "about_me"), ("header-projects.svg", "projects"),
                 ("header-stack.svg", "tech_stack"), ("header-stats.svg", "stats")]:
        header(f, l)
    bio()
    badge("btn-linkedin.svg", "LINKEDIN", CYAN); badge("btn-email.svg", "EMAIL", PINK); badge("btn-github.svg", "GITHUB", GREEN)
    for n, d in PROJECTS:
        card(n, d)
