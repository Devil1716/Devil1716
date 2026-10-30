"""Generate SSS profile SVGs. Live stats come from the GitHub API (GITHUB_TOKEN)."""
import base64, io, json, os, datetime, urllib.request
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "sss"; OUT.mkdir(parents=True, exist_ok=True)
USER = "Devil1716"
F = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Courier New',monospace"
RARE, EPIC, LEG = "#3b82f6", "#a855f7", "#f5c518"
BG, PANEL, PURP, PINK, CYAN, GRN, TXT, DIM, YEL = "#07051a", "#0e0b2b", "#a78bfa", "#ff4fd8", "#22d3ee", "#39d353", "#e2e8f0", "#7c7aa8", "#facc15"

def api(url, data=None):
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    h = {"User-Agent": USER, "Accept": "application/vnd.github+json"}
    if tok: h["Authorization"] = f"Bearer {tok}"
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None, headers=h)
    return json.load(urllib.request.urlopen(req, timeout=30))

def gh(url, data=None):
    try: return api(url, data)
    except Exception:
        import subprocess
        if data: return json.loads(subprocess.run(["gh","api","graphql","-f","query="+data["query"]],capture_output=True,text=True).stdout)
        return json.loads(subprocess.run(["gh","api",url.replace("https://api.github.com/","")],capture_output=True,text=True).stdout)

def stats():
    c = os.environ.get("SSS_CACHE")
    if c and os.path.exists(c): return json.load(open(c))
    st = _stats()
    if c: json.dump(st, open(c, "w"))
    return st

def _stats():
    st = dict(repos="?", followers="?", commits="?", prs="?", streak="?", langs=[], nlang="?")
    try:
        u = gh(f"https://api.github.com/users/{USER}")
        st.update(repos=u["public_repos"], followers=u["followers"])
        repos = gh(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner") + gh(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner&page=2")
        tot = {}
        for r in repos:
            if r["fork"]: continue
            try:
                for k, v in gh(r["languages_url"]).items(): tot[k] = tot.get(k, 0) + v
            except Exception: pass
        skip = {"HTML", "CSS", "Jupyter Notebook", "Shell", "Batchfile", "Makefile", "Dockerfile", "PowerShell", "CMake", "C++", "Swift", "Objective-C", "Ruby", "C"}
        langs = sorted(((k, v) for k, v in tot.items() if k not in skip), key=lambda x: -x[1])[:6]
        T = sum(v for _, v in langs) or 1
        st["langs"] = [(k, v / T) for k, v in langs]; st["nlang"] = len(tot)
    except Exception: pass
    try:
        q = {"query": '{user(login:"%s"){contributionsCollection{totalPullRequestContributions contributionCalendar{totalContributions weeks{contributionDays{contributionCount}}}}}}' % USER}
        cc = gh("https://api.github.com/graphql", q)["data"]["user"]["contributionsCollection"]
        st["commits"] = cc["contributionCalendar"]["totalContributions"]; st["prs"] = cc["totalPullRequestContributions"]
        days = [d["contributionCount"] for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
        best = cur = 0
        for d in days:
            cur = cur + 1 if d else 0; best = max(best, cur)
        st["streak"] = best
    except Exception: pass
    return st

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def svg(w, h, body, extra=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}" shape-rendering="crispEdges">
<style>text{{font-family:{F};}} .glow{{filter:url(#g)}} {extra}</style>
<defs><filter id="g" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="2" fill="#ffffff" opacity="0.025"/></pattern></defs>
{body}
<rect width="{w}" height="{h}" fill="url(#scan)" pointer-events="none"/>
</svg>'''

def frame(w, h, c1=PURP, c2=PINK):
    # pixel border: chunky double stroke with notched corners
    return (f'<rect x="4" y="4" width="{w-8}" height="{h-8}" fill="{BG}"/>'
            f'<rect x="4" y="4" width="{w-8}" height="{h-8}" fill="none" stroke="{c1}" stroke-width="4"/>'
            f'<rect x="12" y="12" width="{w-24}" height="{h-24}" fill="none" stroke="{c2}" stroke-width="2" opacity=".5"/>'
            + "".join(f'<rect x="{x}" y="{y}" width="8" height="8" fill="#0d1117"/>' for x, y in [(0,0),(w-8,0),(0,h-8),(w-8,h-8)]))

def avatar_b64():
    """Sharan's exact GitHub profile photo, embedded unchanged at native resolution."""
    return base64.b64encode((OUT / "avatar.png").read_bytes()).decode()

def hero(st):
    W, H = 1000, 440
    born = datetime.date(2023, 11, 3)
    days = (datetime.date.today() - born).days
    lines = [
        ("sharan", "@devil1716", None),
        ("", "─" * 26, None),
        ("OS", "Agentic AI x86_64", CYAN),
        ("Host", "Amity University Bengaluru", CYAN),
        ("Kernel", "Python 3 / Kotlin", CYAN),
        ("Uptime", f"{days // 365}y {min((days % 365)//30, 11)}m on GitHub", CYAN),
        ("Shell", "FastAPI + Android + LLMs", CYAN),
        ("Role", "Technical Lead @ Quickoo", CYAN),
        ("Class", "B.Tech AI/ML (May 2027)", CYAN),
        ("Packages", f"{st['repos']} repos  ·  {st['nlang']} languages", PINK),
        ("Commits", f"{st['commits']} contributions this year", PINK),
        ("PRs", f"{st['prs']} pull requests this year", PINK),
        ("Streak", f"{st['streak']} day best run", PINK),
        ("Status", "open to remote Backend / Agentic AI interns", GRN),
    ]
    lines = [l for l in lines if not str(l[1]).startswith(("0 ", "? "))]
    import math
    lvl = math.isqrt(st['commits']) if isinstance(st['commits'], int) else 1
    b = [frame(W, H), '<g class="crt">']
    b.append(f'<rect x="4" y="4" width="{W-8}" height="30" fill="{PANEL}"/>')
    for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        b.append(f'<rect x="{22+i*20}" y="14" width="12" height="12" fill="{c}"/>')
    b.append(f'<text x="{W/2}" y="25" fill="{DIM}" font-size="13" text-anchor="middle">sharan@white-angel: ~ $ neofetch</text>')
    # avatar
    b.append(f'<rect x="40" y="62" width="336" height="336" fill="none" stroke="{CYAN}" stroke-width="4" class="glow"/>')
    b.append(f'<image x="48" y="70" width="320" height="320" href="data:image/png;base64,{avatar_b64()}"/>')
    b.append(f'<text x="208" y="420" fill="{PINK}" font-size="12" text-anchor="middle" class="glow">PLAYER 1  ·  LVL {lvl}</text>')
    x0, y0, lh = 410, 74, 23
    for i, (k, v, c) in enumerate(lines):
        y = y0 + i*lh; t = 0.25 + i*0.18
        if i == 0:
            txt = f'<tspan fill="{GRN}" font-weight="bold">sharan</tspan><tspan fill="{TXT}">{esc(v)}</tspan>'
        elif not k:
            txt = f'<tspan fill="{DIM}">{v}</tspan>'
        else:
            txt = f'<tspan fill="{c}" font-weight="bold">{k}</tspan><tspan fill="{TXT}">: {esc(v)}</tspan>'
        b.append(f'<clipPath id="c{i}"><rect x="{x0}" y="{y-17}" height="22" width="0"><animate attributeName="width" from="0" to="560" begin="{t:.2f}s" dur="0.5s" fill="freeze" calcMode="discrete" values="0;80;160;240;320;400;480;560" keyTimes="0;.14;.28;.42;.56;.7;.84;1"/></rect></clipPath>')
        b.append(f'<text x="{x0}" y="{y}" font-size="16" clip-path="url(#c{i})">{txt}</text>')
    yb = y0 + len(lines)*lh + 6
    pal = ["#1a1530", PURP, PINK, CYAN, GRN, YEL, "#3b82f6", TXT]
    for i, c in enumerate(pal):
        b.append(f'<rect x="{x0+i*28}" y="{yb}" width="28" height="16" fill="{c}" opacity="0"><animate attributeName="opacity" to="1" begin="{2.9+i*0.06:.2f}s" dur="0.01s" fill="freeze"/></rect>')
    b.append(f'<rect x="{x0+240}" y="{yb}" width="10" height="16" fill="{GRN}" class="glow"><animate attributeName="opacity" values="1;0;1" dur="1s" calcMode="discrete" repeatCount="indefinite"/></rect>')
    b.append('</g>')
    b.append(f'<defs><radialGradient id="vig" cx="50%" cy="50%" r="75%"><stop offset="60%" stop-color="#000" stop-opacity="0"/><stop offset="100%" stop-color="#000" stop-opacity=".55"/></radialGradient>'
             f'<pattern id="scan2" width="3" height="3" patternUnits="userSpaceOnUse"><rect width="3" height="1" fill="#000" opacity=".28"/></pattern></defs>'
             f'<rect x="8" y="8" width="{W-16}" height="{H-16}" fill="url(#scan2)"/><rect x="8" y="8" width="{W-16}" height="{H-16}" fill="url(#vig)"/>')
    return svg(W, H, "\n".join(b), "@keyframes on{0%{transform:scale(1,.004);filter:brightness(4)}35%{transform:scale(1,.004);filter:brightness(4)}55%{transform:scale(1,1);filter:brightness(2)}62%{opacity:.4}70%{opacity:1}78%{opacity:.7}100%{transform:scale(1,1);filter:brightness(1);opacity:1}} .crt{transform-origin:500px 220px;animation:on .9s ease-out 1 both}")

def header(name, num, color):
    W, H = 1000, 64
    b = [f'<rect x="0" y="16" width="{W}" height="36" fill="{PANEL}"/>',
         f'<rect x="0" y="16" width="8" height="36" fill="{color}"/>',
         f'<rect x="0" y="50" width="{W}" height="2" fill="{color}" opacity=".6"/>',
         f'<text x="28" y="41" fill="{DIM}" font-size="15">STAGE {num:02d}</text>',
         f'<text x="120" y="42" fill="{color}" font-size="20" font-weight="bold" class="glow" letter-spacing="3">{esc(name)}</text>']
    for i in range(12):
        b.append(f'<rect x="{W-24-i*16}" y="30" width="8" height="8" fill="{color}" opacity="{0.15+0.07*i:.2f}"><animate attributeName="opacity" values="0.1;1;0.1" dur="1.6s" begin="{i*0.12:.2f}s" repeatCount="indefinite"/></rect>')
    return svg(W, H, "\n".join(b))

SPRITES = {  # 8x8 pixel icons
 "brain": ["..####..",".#....#.","#.#..#.#","#..##..#","#.#..#.#","#......#",".#.##.#.","..#..#.."],
 "phone": [".######.",".#....#.",".#....#.",".#....#.",".#....#.",".#....#.",".######.",".##..##."],
 "code":  ["........",".#....#.","#......#","#..#...#","#...#..#","#......#",".#....#.","........"],
 "trophy":["#.####.#","########",".######.","..####..","...##...","...##...","..####..",".######."],
 "star":  ["...##...","...##...","########",".######.","..####..",".##..##.","##....##","........"],
 "sat":   ["#......#","##....##",".#.##.#.","..####..","..####..",".#.##.#.","##....##","#......#"],
 "chip":  [".#.#.#..","########",".#....#.","##.##.##",".#.##.#.","##....##","########",".#.#.#.."],
}
def sprite(name, x, y, px, color):
    return "".join(f'<rect x="{x+c*px}" y="{y+r*px}" width="{px}" height="{px}" fill="{color}"/>'
                   for r, row in enumerate(SPRITES[name]) for c, ch in enumerate(row) if ch == "#")

def card(name, icon, color, rank, line1, line2, tags, lvl, live=None):
    W, H = 490, 250
    b = [frame(W, H, color, PURP),
         f'<rect x="28" y="30" width="88" height="88" fill="{PANEL}" stroke="{color}" stroke-width="2"/>',
         f'<g class="glow">{sprite(icon, 40, 42, 8, color)}</g>',
         f'<text x="136" y="52" fill="{DIM}" font-size="12" letter-spacing="2">MAIN QUEST</text>',
         f'<text x="{W-30}" y="54" fill="{YEL}" font-size="22" font-weight="bold" text-anchor="end" class="glow">{rank}</text>',
         f'<text x="136" y="82" fill="{TXT}" font-size="24" font-weight="bold">{esc(name)}</text>',
         f'<text x="136" y="108" fill="{color}" font-size="13">{esc(line1)}</text>',
         f'<text x="28" y="150" fill="{TXT}" font-size="15" opacity=".85">{esc(line2)}</text>']
    x = 28
    for t in tags:
        w = len(t)*8.6 + 18
        b.append(f'<rect x="{x}" y="170" width="{w:.0f}" height="24" fill="{PANEL}" stroke="{color}" stroke-width="1.5"/><text x="{x+9}" y="187" fill="{color}" font-size="13">{esc(t)}</text>')
        x += w + 8
    b.append(f'<text x="28" y="222" fill="{DIM}" font-size="12">XP</text><rect x="56" y="212" width="300" height="12" fill="{PANEL}" stroke="{DIM}"/>')
    b.append(f'<rect x="58" y="214" width="{int(296*lvl)}" height="8" fill="{GRN}"><animate attributeName="width" values="0;{int(296*lvl)}" dur="1.6s"/></rect>')
    b.append(f'<text x="{W-30}" y="223" fill="{PINK}" font-size="13" text-anchor="end">▶ PLAY</text>')
    if live: b.append(f'<text x="{W-30}" y="150" fill="{YEL}" font-size="12" text-anchor="end">★ {live[0]}  ·  {live[1]}</text>')
    return svg(W, H, "\n".join(b))

def live(name):
    try:
        r = gh(f"https://api.github.com/repos/{USER}/{name}")
        return (r["stargazers_count"], r["pushed_at"][:10])
    except Exception: return None

def chip(name, lang, color, live=None):
    W, H = 320, 60
    b = [f'<rect x="2" y="2" width="{W-4}" height="{H-4}" fill="{BG}" stroke="{color}" stroke-width="3"/>',
         f'<rect x="14" y="22" width="16" height="16" fill="{color}"/>',
         f'<text x="42" y="30" fill="{TXT}" font-size="15" font-weight="bold">{esc(name)}</text>',
         f'<text x="42" y="47" fill="{DIM}" font-size="12">{esc(lang[:10])} · ★ {live[0] if live else 0} · {live[1] if live else ""}</text>',
         f'<text x="{W-16}" y="36" fill="{color}" font-size="16" text-anchor="end">›</text>']
    return svg(W, H, "\n".join(b))

def achievements():
    W, H = 1000, 300
    items = [
        ("sat", RARE, "ORBITAL OPTICS", "ISRO Bharatiya Antariksh Hackathon", "Challenge 9 · Shack Hartmann wavefront reconstruction", "RARE"),
        ("brain", EPIC, "TINY GIANT", "Novo Nordisk hackathon", "Trained a 200M parameter language model on pharma regulations", "EPIC"),
        ("star", LEG, "PARTY LEADER", "Technical Lead @ Quickoo", "One year leading microservices, backend and the dev team", "LEGENDARY"),
    ]
    b = [frame(W, H, YEL, PURP), f'<text x="36" y="46" fill="{YEL}" font-size="16" letter-spacing="3" class="glow">★ ACHIEVEMENTS 3/3</text>']
    for i, (ic, c, title, what, desc, rar) in enumerate(items):
        y = 66 + i*74; t = 0.4 + i*0.5
        g = [f'<rect x="32" y="{y}" width="936" height="62" fill="{PANEL}" stroke="{c}" stroke-width="2"/>',
             f'<rect x="40" y="{y+7}" width="48" height="48" fill="{BG}" stroke="{c}" stroke-width="2"/>',
             f'<g class="glow">{sprite("trophy", 44, y+11, 5, c)}</g>',
             f'<g fill="#fff">' + "".join(f'<rect x="{sx}" y="{y+sy}" width="3" height="3" opacity="0"><animate attributeName="opacity" values="0;1;0" dur="1.8s" begin="{t+k*0.45:.2f}s" repeatCount="indefinite"/></rect>' for k,(sx,sy) in enumerate([(42,8),(84,14),(46,50),(80,46)])) + '</g>',
             f'<rect x="864" y="{y+12}" width="92" height="20" fill="{c}" fill-opacity=".18" stroke="{c}"/>',
             f'<text x="104" y="{y+26}" fill="{c}" font-size="15" font-weight="bold" letter-spacing="2">{title}</text>',
             f'<text x="104" y="{y+48}" fill="{TXT}" font-size="14">{esc(what)}  <tspan fill="{DIM}">{esc(desc)}</tspan></text>',
             f'<text x="910" y="{y+27}" fill="{c}" font-size="12" font-weight="bold" text-anchor="middle" letter-spacing="1">{rar}</text>',
             f'<text x="950" y="{y+48}" fill="{GRN}" font-size="12" text-anchor="end">UNLOCKED</text>',
             f'<rect x="32" y="{y}" width="60" height="62" fill="#ffffff" opacity=".06"><animate attributeName="x" values="32;908;908" keyTimes="0;.35;1" dur="4s" begin="{t}s" repeatCount="indefinite"/></rect>']
        b.append(f'<g class="ach" style="animation-delay:{t}s">{"".join(g)}</g>')
    return svg(W, H, "\n".join(b), "@keyframes pulse{0%,100%{opacity:1}50%{opacity:.55}} .ach{animation:pulse 2.4s ease-in-out infinite}")

def inventory():
    items = [("PY","Python","#3776ab"),("KT","Kotlin","#a97bff"),("TS","TypeScript","#3178c6"),("FA","FastAPI","#009688"),
             ("AN","Android","#3ddc84"),("DK","Docker","#2496ed"),("RE","React","#61dafb"),("LL","LLMs","#ff4fd8"),
             ("MC","MCP","#facc15"),("ON","ONNX","#a3a3a3"),("PT","PyTorch","#ee4c2c"),("DT","Dart","#0175c2"),
             ("PG","Postgres","#4169e1"),("GT","Git","#f05032"),("LX","Linux","#fcc624"),("GC","GCP","#4285f4")]
    W, H = 1000, 290; cols = 8; s = 104; gap = 12
    x0 = (W - (cols*s + (cols-1)*gap))/2
    b = [frame(W, H, CYAN, PURP), f'<text x="36" y="44" fill="{CYAN}" font-size="16" letter-spacing="3" class="glow">INVENTORY  16/16 slots</text>',
         f'<text x="964" y="44" fill="{DIM}" font-size="12" text-anchor="end">[E] equip</text>']
    for i, (ab, nm, c) in enumerate(items):
        x = x0 + (i % cols)*(s+gap); y = 62 + (i//cols)*(s+8)
        b.append(f'<rect x="{x}" y="{y}" width="{s}" height="{s-8}" fill="{PANEL}" stroke="#2a2550" stroke-width="3"/>'
                 f'<rect x="{x+3}" y="{y+3}" width="{s-6}" height="4" fill="{c}" opacity=".7"/>'
                 f'<text x="{x+s/2}" y="{y+52}" fill="{c}" font-size="30" font-weight="bold" text-anchor="middle" class="glow">{ab}</text>'
                 f'<text x="{x+s/2}" y="{y+80}" fill="{TXT}" font-size="12" text-anchor="middle">{nm}</text>')
    # roving selection cursor
    vals = ";".join(f"{x0 + (i % cols)*(s+gap) - 4:.0f},{62 + (i//cols)*(s+8) - 4}" for i in [0,1,3,4,7,12,9,0])
    b.append(f'<rect width="{s+8}" height="{s}" fill="none" stroke="{YEL}" stroke-width="3" class="glow"><animateMotion values="{vals.replace(";", ";")}" dur="9s" calcMode="discrete" repeatCount="indefinite"/></rect>')
    b[-1] = b[-1].replace(f'values="{vals}"', 'values="' + ";".join(v.replace(",", " ") and v for v in vals.split(";")) + '"')
    return svg(W, H, "\n".join(b))

def footer(st):
    W, H = 1000, 170
    b = [frame(W, H, PINK, CYAN),
         f'<text x="{W/2}" y="68" fill="{PINK}" font-size="34" font-weight="bold" text-anchor="middle" letter-spacing="6" class="glow">PRESS START<animate attributeName="opacity" values="1;1;0;0" dur="1.2s" repeatCount="indefinite"/></text>',
         f'<text x="{W/2}" y="104" fill="{TXT}" font-size="15" text-anchor="middle">INSERT COIN: inspect and cheer player 1\'s repos</text>',
         f'<text x="40" y="146" fill="{YEL}" font-size="13">CREDITS {st["commits"]}</text>',
         f'<text x="{W/2}" y="146" fill="{DIM}" font-size="13" text-anchor="middle">© 2026 PLAYER 1 · DEVIL1716</text>',
         f'<text x="{W-40}" y="146" fill="{CYAN}" font-size="13" text-anchor="end">HI SCORE SHARAN</text>',
         f'<g>{sprite("star", 120, 52, 4, YEL)}<animateTransform attributeName="transform" type="translate" values="0 0;0 -6;0 0" dur="1s" repeatCount="indefinite"/></g>',
         f'<g>{sprite("star", 848, 52, 4, YEL)}<animateTransform attributeName="transform" type="translate" values="0 -6;0 0;0 -6" dur="1s" repeatCount="indefinite"/></g>']
    return svg(W, H, "\n".join(b))

def quest():
    W, H = 1000, 250
    b = [frame(W, H, PINK, PURP),
         f'<text x="36" y="48" fill="{PINK}" font-size="16" letter-spacing="3" class="glow">⚔ CURRENT QUEST</text>',
         f'<text x="964" y="48" fill="{DIM}" font-size="12" text-anchor="end">BOSS ENCOUNTER</text>',
         f'<text x="36" y="92" fill="{TXT}" font-size="26" font-weight="bold">ON DEVICE AGENT WARDEN</text>',
         f'<text x="36" y="118" fill="{DIM}" font-size="14">Agentic AI that plans, taps and recovers on a real phone. No cloud, no excuses.</text>',
         f'<text x="36" y="155" fill="{YEL}" font-size="12">BOSS HP</text>',
         f'<rect x="100" y="142" width="560" height="16" fill="{PANEL}" stroke="{DIM}"/>',
         f'<rect x="102" y="144" width="556" height="12" fill="{PINK}"><animate attributeName="width" values="556;556;390;390;212;212;556" keyTimes="0;.1;.18;.45;.53;.9;1" dur="8s" repeatCount="indefinite"/></rect>',
         f'<text x="672" y="156" fill="{YEL}" font-size="12" font-weight="bold">CRITICAL HIT<animate attributeName="opacity" values="0;0;1;0;0;1;0;0" keyTimes="0;.1;.14;.2;.45;.5;.56;1" dur="8s" repeatCount="indefinite"/></text>',
         f'<g class="glow">{sprite("chip", 860, 70, 9, PINK)}<animateTransform attributeName="transform" type="translate" values="0 0;0 -5;0 0" dur="1.4s" repeatCount="indefinite"/></g>',
         f'<rect x="36" y="184" width="928" height="40" fill="{PANEL}" stroke="{GRN}" stroke-width="2"/>',
         f'<text x="56" y="209" fill="{GRN}" font-size="15" font-weight="bold">SEEKING GUILD</text>',
         f'<text x="200" y="209" fill="{TXT}" font-size="15">remote Backend / Agentic AI internship</text>',
         f'<text x="944" y="209" fill="{YEL}" font-size="14" text-anchor="end" class="glow">▶ RECRUIT ME<animate attributeName="opacity" values="1;.35;1" dur="1.2s" repeatCount="indefinite"/></text>']
    return svg(W, H, "\n".join(b))

LC = {"TypeScript":"#3178c6","Kotlin":"#a97bff","JavaScript":"#f1e05a","Go":"#00add8","Python":"#3776ab","Java":"#b07219","Dart":"#0175c2","Rust":"#dea584"}
def langs(st):
    L = st.get("langs") or []
    W, H = 1000, 90 + 34*max(len(L), 1)
    b = [frame(W, H, GRN, PURP), f'<text x="36" y="48" fill="{GRN}" font-size="16" letter-spacing="3" class="glow">PLAYER STATS</text>',
         f'<text x="964" y="48" fill="{DIM}" font-size="12" text-anchor="end">live from repo language bytes</text>']
    top = max([v for _, v in L] or [1])
    for i, (k, v) in enumerate(L):
        y = 66 + i*34; c = LC.get(k, CYAN); n = max(1, round(40*v/top))
        b.append(f'<text x="36" y="{y+17}" fill="{c}" font-size="14" font-weight="bold">{esc(k.upper()[:10])}</text>')
        for j in range(40):
            on = j < n
            b.append(f'<rect x="{190+j*17}" y="{y+4}" width="13" height="16" fill="{c if on else PANEL}"' + (f' opacity="0"><animate attributeName="opacity" values="0;1" dur="0.05s" begin="{0.3+i*0.15+j*0.02:.2f}s" fill="freeze"/></rect>' if on else '/>'))
        b.append(f'<text x="964" y="{y+17}" fill="{TXT}" font-size="14" text-anchor="end">{v*100:.0f}%</text>')
    return svg(W, H, "\n".join(b))

def ach_item(i):
    import re as _re
    W, H = 1000, 84
    items = ACH
    ic, c, title, what, desc, rar = items[i]; y = 10; t = 0.3 + i*0.4
    g = [f'<rect x="4" y="{y}" width="992" height="66" fill="{PANEL}" stroke="{c}" stroke-width="3"/>',
         f'<rect x="4" y="{y}" width="8" height="66" fill="{c}"/>',
         f'<rect x="26" y="{y+9}" width="48" height="48" fill="{BG}" stroke="{c}" stroke-width="2"/>',
         f'<g class="glow">{sprite("trophy", 30, y+13, 5, c)}</g>',
         f'<g fill="#fff">' + "".join(f'<rect x="{sx}" y="{y+sy}" width="4" height="4" opacity="0"><animate attributeName="opacity" values="0;1;0" dur="1.8s" begin="{t+k*0.45:.2f}s" repeatCount="indefinite"/></rect>' for k,(sx,sy) in enumerate([(24,6),(72,12),(30,54),(70,50)])) + '</g>',
         f'<text x="94" y="{y+28}" fill="{c}" font-size="16" font-weight="bold" letter-spacing="2">{title}</text>',
         f'<text x="94" y="{y+50}" fill="{TXT}" font-size="14">{esc(what)}  <tspan fill="{DIM}">{esc(desc)}</tspan></text>',
         f'<rect x="854" y="{y+12}" width="120" height="22" fill="{c}" fill-opacity=".18" stroke="{c}"/>',
         f'<text x="914" y="{y+28}" fill="{c}" font-size="12" font-weight="bold" text-anchor="middle" letter-spacing="2">{rar}</text>',
         f'<text x="974" y="{y+54}" fill="{GRN}" font-size="12" text-anchor="end">UNLOCKED ✓</text>',
         f'<rect x="12" y="{y+3}" width="40" height="60" fill="#fff" opacity=".07"><animate attributeName="x" values="12;950;950" keyTimes="0;.35;1" dur="4s" begin="{t}s" repeatCount="indefinite"/></rect>']
    return svg(W, H, "".join(g))

ACH = [
    ("sat", RARE, "ORBITAL OPTICS", "ISRO Bharatiya Antariksh Hackathon", "Challenge 9 · wavefront reconstruction", "RARE"),
    ("brain", EPIC, "TINY GIANT", "Novo Nordisk hackathon", "200M parameter language model", "EPIC"),
    ("star", LEG, "PARTY LEADER", "Technical Lead @ Quickoo", "microservices, backend and the dev team", "LEGENDARY"),
]
INV = [("PY","Python","#3776ab","https://www.python.org"),("KT","Kotlin","#a97bff","https://kotlinlang.org"),("TS","TypeScript","#3178c6","https://www.typescriptlang.org"),("FA","FastAPI","#009688","https://fastapi.tiangolo.com"),
       ("AN","Android","#3ddc84","https://developer.android.com"),("DK","Docker","#2496ed","https://www.docker.com"),("RE","React","#61dafb","https://react.dev"),("LL","LLMs","#ff4fd8","https://huggingface.co"),
       ("MC","MCP","#facc15","https://modelcontextprotocol.io"),("ON","ONNX","#a3a3a3","https://onnx.ai"),("PT","PyTorch","#ee4c2c","https://pytorch.org"),("DT","Dart","#0175c2","https://dart.dev"),
       ("PG","Postgres","#4169e1","https://www.postgresql.org"),("GT","Git","#f05032","https://git-scm.com"),("LX","Linux","#fcc624","https://kernel.org"),("GC","GCP","#4285f4","https://cloud.google.com")]
def inv_tile(ab, nm, c, i):
    s = 116
    return svg(s, s, f'<rect x="3" y="3" width="{s-6}" height="{s-6}" fill="{PANEL}" stroke="#2a2550" stroke-width="4"/>'
        f'<rect x="7" y="7" width="{s-14}" height="5" fill="{c}"/>'
        f'<text x="{s/2}" y="62" fill="{c}" font-size="32" font-weight="bold" text-anchor="middle" class="glow">{ab}</text>'
        f'<text x="{s/2}" y="92" fill="{TXT}" font-size="13" text-anchor="middle">{nm}</text>'
        f'<rect x="3" y="3" width="{s-6}" height="{s-6}" fill="none" stroke="{YEL}" stroke-width="4" opacity="0"><animate attributeName="opacity" values="0;1;0;0" keyTimes="0;.03;.07;1" dur="9.6s" begin="{i*0.6:.1f}s" repeatCount="indefinite"/></rect>')

def main():
    st = stats()
    (OUT/"hero-fetch.svg").write_text(hero(st))
    for name, n, c in [("WHOAMI", 1, CYAN), ("CURRENT QUEST", 2, PINK), ("MAIN QUESTS", 3, PURP), ("ACHIEVEMENTS", 4, YEL), ("INVENTORY", 5, GRN), ("REPO ARCADE", 6, CYAN), ("BATTLE LOG", 7, PURP)]:
        (OUT/f"h-{n}.svg").write_text(header(name, n, c))
    cards = [
        ("CognyxOS", "chip", PURP, "S", "an operating layer for AI agents", "Agents that plan, act and recover.", ["Python","Agents","LLMs"], .9),
        ("agent-phone-app", "phone", GRN, "S", "Gemma first agent phone app", "Agent that drives a real phone.", ["Kotlin","Gemma","Android"], .85),
        ("AgentIDE", "code", CYAN, "A", "an IDE where agents write the code", "Agent native editor with live runs.", ["TypeScript","MCP","React"], .75),
        ("BubbleLab", "brain", PINK, "A", "workflow automation for developers", "Open source flows you can export.", ["TypeScript","Workflows","OSS"], .7),
    ]
    for c in cards: (OUT/f"q-{c[0]}.svg").write_text(card(*c, live=live(c[0])))
    for n, l, c in [("arbor-dashboard","TypeScript","#3178c6"),("isro-bah-challenge9-shwfs","Python","#3776ab"),("quicko-microservices","Microservices","#e34c26"),
                    ("drapesense","JavaScript","#f1e05a"),("kosh","Dart","#0175c2"),("bluetooth-manet-android","Kotlin","#a97bff")]:
        (OUT/f"s-{n}.svg").write_text(chip(n, l, c, live(n)))
    (OUT/"footer.svg").write_text(footer(st))
    for i in range(3): (OUT/f"ach-{i+1}.svg").write_text(ach_item(i))
    for i,(ab,nm,c,_) in enumerate(INV): (OUT/f"inv-{ab}.svg").write_text(inv_tile(ab,nm,c,i))
    (OUT/"quest.svg").write_text(quest())
    (OUT/"langs.svg").write_text(langs(st))
    print(st)

if __name__ == "__main__": main()
