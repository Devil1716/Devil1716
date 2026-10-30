"""Player 1 arcade: visitors interact with Sharan's real GitHub repos through issue titles.
Only the issue title and author login are read, each matched by strict regexes and allowlists.
No eval, no shell, nothing from the issue body is used."""
import datetime, json, os, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sss import gh, svg, frame, esc, sprite, F, BG, PANEL, PURP, PINK, CYAN, GRN, TXT, DIM, YEL

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "game" / "arcade.json"
OUT = ROOT / "assets" / "arcade"
README = ROOT / "README.md"
USER, REPO = "Devil1716", "Devil1716/Devil1716"
API = "https://api.github.com"
# Allowlist: public, non fork repos. Checked again against the live API before use.
REPOS = ["CognyxOS", "agent-phone-app", "AgentIDE", "arbor-dashboard", "isro-bah-challenge9-shwfs", "quicko-microservices",
         "drapesense", "kosh", "bluetooth-manet-android", "plot-ledger", "HackerRank-Orchestrator", "open-bugbot"]
OPTIONS = {  # boss raid: what player 1 builds next
    "voice": ("VOICE AGENT", "a voice first agent for the phone app"),
    "mcp": ("MCP TOOLBELT", "MCP servers for CognyxOS"),
    "ide": ("AGENTIDE V2", "multi agent runs inside AgentIDE"),
    "offline": ("OFFLINE LLM", "a tiny on device model that runs offline"),
}
LANG_C = {"Python": "#3776ab", "Kotlin": "#a97bff", "TypeScript": "#3178c6", "JavaScript": "#f1e05a", "Dart": "#0175c2",
          "HTML": "#e34c26", "CSS": "#663399", "Shell": "#89e051", "Java": "#b07219", "C": "#555555"}
TITLE = re.compile(r"^gh\|(inspect|cheer)\|([A-Za-z0-9._-]{1,100})$|^gh\|vote\|([a-z]{1,10})$")
LOGIN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")
ISSUE = "https://github.com/" + REPO + "/issues/new?title={t}&body=Just+press+Submit+new+issue.+The+arcade+bot+does+the+rest."

def today(): return os.environ.get("ARCADE_TODAY") or datetime.date.today().isoformat()

def load():
    base = {"xp": {}, "cheerers": {}, "cheers": {}, "votes": {}, "voters": {}, "inspect": None, "log": []}
    if STATE.exists(): base.update(json.loads(STATE.read_text()))
    return base

def repo_info(name):
    """Live data for one allowlisted repo. Returns None if it is not a public non fork repo."""
    r = gh(f"{API}/repos/{USER}/{name}")
    if not isinstance(r, dict) or r.get("fork") or r.get("private") or r.get("name") != name: return None
    langs = gh(f"{API}/repos/{USER}/{name}/languages") or {}
    commits = gh(f"{API}/repos/{USER}/{name}/commits?per_page=100") or []
    commits = commits if isinstance(commits, list) else []
    days = [0] * 12  # commits per week, last 12 weeks
    now = datetime.datetime.now(datetime.timezone.utc)
    for c in commits:
        d = datetime.datetime.fromisoformat(c["commit"]["committer"]["date"].replace("Z", "+00:00"))
        w = (now - d).days // 7
        if w < 12: days[11 - w] += 1
    last = commits[0]["commit"] if commits else None
    return {"name": name, "stars": r["stargazers_count"], "forks": r["forks_count"], "issues": r["open_issues_count"],
            "desc": (r.get("description") or "No description yet.")[:90], "lang": r.get("language") or "Mixed",
            "langs": langs if isinstance(langs, dict) else {}, "spark": days,
            "msg": (last["message"].splitlines()[0][:60] if last else "no commits"),
            "date": (last["committer"]["date"][:10] if last else r["pushed_at"][:10]), "url": r["html_url"]}

def handle(st, title, user, info=repo_info):
    """Apply one issue. Returns (comment, changed)."""
    if not LOGIN.match(user or ""): return "Unknown player.", False
    m = TITLE.match((title or "").strip())
    if not m: return "I could not read that command. Use the buttons on the profile.", False
    act, name, opt = m.group(1), m.group(2), m.group(3)
    if opt is not None:
        if opt not in OPTIONS: return "That raid target does not exist. Pick one of the boss buttons.", False
        prev = st["voters"].get(user)
        if prev == opt: return f"You already back {OPTIONS[opt][0]}. One vote per player.", False
        if prev: st["votes"][prev] = max(0, st["votes"].get(prev, 0) - 1)
        st["voters"][user] = opt; st["votes"][opt] = st["votes"].get(opt, 0) + 1
        st["log"].append(f"@{user} hit {OPTIONS[opt][0]}")
        return (f"Vote moved to {OPTIONS[opt][0]}." if prev else f"Your hit landed on {OPTIONS[opt][0]}.") + f" It now has {st['votes'][opt]} votes.", True
    if name not in REPOS: return "That repo is not in the quest menu. Pick one of the repo buttons.", False
    data = info(name)
    if not data: return "That repo is not available right now.", False
    if act == "inspect":
        st["inspect"] = data; st["log"].append(f"@{user} inspected {name}")
        top = ", ".join(sorted(data["langs"], key=lambda k: -data["langs"][k])[:3]) or data["lang"]
        return (f"### {name}\n{data['desc']}\n\nStars {data['stars']}, forks {data['forks']}, open issues {data['issues']}\n\n"
                f"Languages: {top}\n\nLast commit on {data['date']}: `{data['msg'].replace('`', '')}`\n\n"
                f"[Open the repo]({data['url']}) and star it to grant +100 XP."), True
    key = f"{user}|{name}"
    if st["cheers"].get(key) == today(): return f"You already cheered {name} today. Come back tomorrow, or star it for +100 XP.", False
    st["cheers"][key] = today()
    st["xp"][name] = st["xp"].get(name, 0) + 10
    st["cheerers"][user] = st["cheerers"].get(user, 0) + 1
    st["log"].append(f"@{user} cheered {name}")
    return f"{name} gained +10 XP and is now at {st['xp'][name]} XP. Star the repo for +100 XP: https://github.com/{USER}/{name}", True

# ---------- rendering ----------
def bar(x, y, w, h, frac, color, delay=0):
    fw = max(0, int((w - 4) * frac))
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{PANEL}" stroke="{DIM}"/>'
            + "".join(f'<rect x="{x+2+i}" y="{y+2}" width="6" height="{h-4}" fill="{color}" opacity="0"><animate attributeName="opacity" to="1" begin="{delay+i/600:.2f}s" dur=".05s" fill="freeze"/></rect>'
                      for i in range(0, fw - 5, 8)))

def inspect_svg(d, stars_bonus):
    W, H = 1000, 300
    b = [frame(W, H, CYAN, PURP), f'<text x="36" y="48" fill="{CYAN}" font-size="15" letter-spacing="3" class="glow">🔍 INSPECT CARD</text>']
    if not d:
        b.append(f'<text x="{W/2}" y="160" fill="{DIM}" font-size="20" text-anchor="middle">Pick a repo below to inspect it live<animate attributeName="opacity" values="1;.3;1" dur="1.4s" repeatCount="indefinite"/></text>')
        return svg(W, H, "".join(b))
    c = LANG_C.get(d["lang"], PINK)
    b += [f'<text x="964" y="48" fill="{DIM}" font-size="12" text-anchor="end">LIVE FROM GITHUB</text>',
          f'<text x="36" y="90" fill="{TXT}" font-size="28" font-weight="bold">{esc(d["name"])}</text>',
          f'<text x="36" y="116" fill="{DIM}" font-size="14">{esc(d["desc"])}</text>']
    for i, (lab, v, col) in enumerate([("STARS", d["stars"], YEL), ("FORKS", d["forks"], CYAN), ("ISSUES", d["issues"], PINK), ("XP", stars_bonus, GRN)]):
        x = 36 + i * 150
        b.append(f'<rect x="{x}" y="134" width="136" height="56" fill="{PANEL}" stroke="{col}" stroke-width="2"/><text x="{x+12}" y="154" fill="{DIM}" font-size="11">{lab}</text><text x="{x+12}" y="181" fill="{col}" font-size="22" font-weight="bold">{v}</text>')
    tot = sum(d["langs"].values()) or 1; x = 36
    for k, v in sorted(d["langs"].items(), key=lambda t: -t[1])[:5]:
        w = int(560 * v / tot)
        if w < 2: continue
        b.append(f'<rect x="{x}" y="208" width="{w}" height="14" fill="{LANG_C.get(k, PURP)}"/>')
        if w > 70: b.append(f'<text x="{x+4}" y="238" fill="{DIM}" font-size="11">{esc(k)}</text>')
        x += w
    b.append(f'<text x="36" y="268" fill="{GRN}" font-size="13">LAST COMMIT {d["date"]}  ›  {esc(d["msg"])}</text>')
    mx = max(d["spark"]) or 1
    b.append(f'<text x="680" y="150" fill="{DIM}" font-size="11">COMMITS, LAST 12 WEEKS</text>')
    for i, v in enumerate(d["spark"]):
        h = int(70 * v / mx) if v else 2
        b.append(f'<rect x="{680+i*24}" y="{232-h}" width="18" height="{h}" fill="{c if v else DIM}"><animate attributeName="height" values="0;{h}" dur=".8s"/><animate attributeName="y" values="232;{232-h}" dur=".8s"/></rect>')
    return svg(W, H, "".join(b))

def xp_svg(st):
    W = 1000; rows = sorted(REPOS, key=lambda r: -st["xp"].get(r, 0))[:6]; H = 90 + 36 * len(rows) + 120
    mx = max([st["xp"].get(r, 0) for r in rows] + [100])
    b = [frame(W, H, GRN, PURP), f'<text x="36" y="48" fill="{GRN}" font-size="15" letter-spacing="3" class="glow">⬆ LEVEL UP BOARD</text>',
         f'<text x="964" y="48" fill="{DIM}" font-size="12" text-anchor="end">CHEER +10 XP · STAR +100 XP</text>']
    for i, r in enumerate(rows):
        y = 80 + i * 36; xp = st["xp"].get(r, 0) + 100 * st.get("stars", {}).get(r, 0)
        b.append(f'<text x="36" y="{y+16}" fill="{YEL if i == 0 else TXT}" font-size="14">{i+1}. {esc(r[:24])}</text>')
        b.append(bar(330, y, 520, 20, xp / max(mx, xp, 1), GRN if i else YEL, i * .15))
        b.append(f'<text x="964" y="{y+16}" fill="{TXT}" font-size="13" text-anchor="end">LV {xp//100+1} · {xp}</text>')
    y = 100 + 36 * len(rows)
    b.append(f'<text x="36" y="{y}" fill="{PINK}" font-size="13" letter-spacing="2">TOP CHEERERS</text>')
    top = sorted(st["cheerers"].items(), key=lambda t: (-t[1], t[0]))[:5]
    if not top: b.append(f'<text x="36" y="{y+30}" fill="{DIM}" font-size="14">No cheers yet. Be the first hero.</text>')
    for i, (u, n) in enumerate(top):
        b.append(f'<text x="{36+i*186}" y="{y+30}" fill="{TXT}" font-size="13">{"🥇🥈🥉"[i] if i < 3 else "★"} @{esc(u[:14])} {n}</text>')
    return svg(W, H, "".join(b))

def raid_svg(st):
    W, H = 1000, 90 + 52 * len(OPTIONS) + 20
    tot = sum(st["votes"].values())
    b = [frame(W, H, PINK, YEL), f'<text x="36" y="48" fill="{PINK}" font-size="15" letter-spacing="3" class="glow">⚔ BOSS RAID</text>',
         f'<text x="964" y="48" fill="{DIM}" font-size="12" text-anchor="end">{tot} HITS · MOST DAMAGE GETS BUILT NEXT</text>']
    lead = max(OPTIONS, key=lambda k: st["votes"].get(k, 0)) if tot else None
    for i, (k, (nm, desc)) in enumerate(OPTIONS.items()):
        y = 76 + i * 52; v = st["votes"].get(k, 0); hp = 1 - v / max(tot, 1) if tot else 1
        b.append(f'<text x="36" y="{y+18}" fill="{YEL if k == lead else TXT}" font-size="15" font-weight="bold">{nm}</text><text x="36" y="{y+36}" fill="{DIM}" font-size="11">{esc(desc)}</text>')
        b.append(f'<text x="360" y="{y+22}" fill="{DIM}" font-size="11">HP</text>' + bar(386, y + 8, 460, 20, hp, PINK if hp > .4 else YEL, i * .15))
        b.append(f'<text x="964" y="{y+24}" fill="{TXT}" font-size="13" text-anchor="end">{v} hits</text>')
    return svg(W, H, "".join(b))

def radar_svg(events):
    W, H = 1000, 90 + 34 * max(1, len(events)) + 10
    b = [frame(W, H, PURP, CYAN), f'<text x="36" y="48" fill="{PURP}" font-size="15" letter-spacing="3" class="glow">📡 COMMIT RADAR</text>',
         f'<text x="964" y="48" fill="{DIM}" font-size="12" text-anchor="end">LIVE QUEST LOG · UPDATED {today()}</text>']
    if not events: b.append(f'<text x="36" y="100" fill="{DIM}" font-size="14">Radar is quiet. Player 1 is probably cooking something.</text>')
    for i, (icon, col, text, when) in enumerate(events):
        y = 86 + i * 34
        b.append(f'<g opacity="0"><animate attributeName="opacity" to="1" begin="{i*.35:.2f}s" dur=".2s" fill="freeze"/>'
                 f'<rect x="36" y="{y}" width="10" height="10" fill="{col}"/><text x="58" y="{y+10}" fill="{col}" font-size="13" font-weight="bold">{icon}</text>'
                 f'<text x="150" y="{y+10}" fill="{TXT}" font-size="14">{esc(text[:80])}</text><text x="964" y="{y+10}" fill="{DIM}" font-size="12" text-anchor="end">{when}</text></g>')
    return svg(W, H, "".join(b))

def fetch_events():
    ev = gh(f"{API}/users/{USER}/events/public?per_page=50") or []
    out = []
    for e in ev if isinstance(ev, list) else []:
        r, p, t = e["repo"]["name"].split("/")[-1], e.get("payload", {}), e["type"]
        if t == "PushEvent":
            n = p.get("size") or len(p.get("commits") or []) or 1
            msg = ((p.get("commits") or [{}])[-1].get("message") or "").splitlines()[0:1]
            out.append(("PUSH", GRN, f"{r}: {n} commit{'s' if n != 1 else ''}" + (f", {msg[0]}" if msg else "")))
        elif t == "PullRequestEvent": out.append(("PR", PINK, f"{r}: {p.get('action')} PR #{p.get('number')}"))
        elif t == "CreateEvent" and p.get("ref_type") == "repository": out.append(("NEW REPO", YEL, f"spawned {r}"))
        elif t == "CreateEvent": out.append(("BRANCH", CYAN, f"{r}: new {p.get('ref_type')} {p.get('ref') or ''}"))
        elif t == "ReleaseEvent": out.append(("RELEASE", YEL, f"{r}: {p.get('release', {}).get('tag_name', '')}"))
        elif t == "WatchEvent": out.append(("STAR", YEL, f"starred {e['repo']['name']}"))
        else: continue
        out[-1] = out[-1] + (e["created_at"][:10],)
        if len(out) == 5: break
    return out

def btn(label, color, w):
    return svg(w, 44, f'<rect x="2" y="2" width="{w-4}" height="40" fill="{PANEL}" stroke="{color}" stroke-width="3"/>'
                      f'<text x="{w/2}" y="28" fill="{color}" font-size="14" font-weight="bold" text-anchor="middle">{esc(label)}</text>')

def link(t): return ISSUE.format(t=t.replace("|", "%7C"))

def block(st):
    menu = " ".join(f'<a href="{link("gh|inspect|"+r)}"><img src="./assets/arcade/r-{r}.svg" width="24%" alt="Inspect {r}" /></a>' for r in REPOS)
    cheer = " ".join(f'<a href="{link("gh|cheer|"+r)}"><img src="./assets/arcade/c-{r}.svg" width="24%" alt="Cheer {r}" /></a>' for r in REPOS)
    raid = " ".join(f'<a href="{link("gh|vote|"+k)}"><img src="./assets/arcade/v-{k}.svg" width="24%" alt="Hit {v[0]}" /></a>' for k, v in OPTIONS.items())
    ins = st["inspect"]["name"] if st["inspect"] else None
    star = f'<a href="https://github.com/{USER}/{ins}"><img src="./assets/arcade/star.svg" height="40" alt="Star to grant +100 XP" /></a>' if ins else ""
    log = "".join(f"<li>{esc(x)}</li>" for x in reversed(st["log"][-8:])) or "<li>No moves yet.</li>"
    return (f'<!--ARCADE:START-->\n<a id="arcade"></a>\n\n<img src="./assets/arcade/inspect.svg" width="100%" alt="Inspect card for {ins or "no repo yet"}" />\n\n{star}\n\n'
            f'<b>REPO QUEST</b>: pick a repo, press Submit, and its live card loads here.\n\n{menu}\n\n'
            f'<a id="levelup"></a><img src="./assets/arcade/xp.svg" width="100%" alt="Level up board: most cheered repos and top cheerers" />\n\n'
            f'<details><summary><b>⬆ CHEER A REPO (+10 XP, once a day each)</b></summary>\n<br />\n\n{cheer}\n</details>\n\n'
            f'<img src="./assets/arcade/raid.svg" width="100%" alt="Boss raid poll: what Sharan builds next" />\n\n{raid}\n\n'
            f'<img src="./assets/arcade/radar.svg" width="100%" alt="Commit radar: Sharan\'s latest public GitHub activity" />\n\n'
            f'<details><summary><b>📜 ARCADE LOG</b></summary>\n<ul>{log}</ul>\n</details>\n<!--ARCADE:END-->')

def render(st, events=None):
    OUT.mkdir(parents=True, exist_ok=True)
    for r in REPOS:
        (OUT / f"r-{r}.svg").write_text(btn("▶ " + (r if len(r) <= 22 else r[:20] + ".."), CYAN, 240))
        (OUT / f"c-{r}.svg").write_text(btn("+XP " + (r if len(r) <= 20 else r[:18] + ".."), GRN, 240))
    for k, (nm, _) in OPTIONS.items(): (OUT / f"v-{k}.svg").write_text(btn("⚔ " + nm, PINK, 240))
    (OUT / "star.svg").write_text(btn("★ STAR TO GRANT +100 XP", YEL, 300))
    ins = st["inspect"]
    (OUT / "inspect.svg").write_text(inspect_svg(ins, st["xp"].get(ins["name"], 0) + 100 * ins["stars"] if ins else 0))
    (OUT / "xp.svg").write_text(xp_svg(st))
    (OUT / "raid.svg").write_text(raid_svg(st))
    if events is not None: (OUT / "radar.svg").write_text(radar_svg(events))
    md = README.read_text()
    README.write_text(re.sub(r"<!--ARCADE:START-->.*?<!--ARCADE:END-->", lambda _: block(st), md, flags=re.S))

def refresh_stars(st):
    """Daily: stars per repo feed the XP board."""
    st["stars"] = {}
    for r in REPOS:
        d = gh(f"{API}/repos/{USER}/{r}")
        if isinstance(d, dict) and "stargazers_count" in d: st["stars"][r] = d["stargazers_count"]

def save(st):
    st["log"] = st["log"][-50:]
    STATE.parent.mkdir(exist_ok=True); STATE.write_text(json.dumps(st, indent=1, sort_keys=True))

def main():
    title, user = os.environ.get("ISSUE_TITLE", ""), os.environ.get("ISSUE_USER", "")
    st = load()
    if title:
        msg, changed = handle(st, title, user)
        if changed: save(st); render(st)
    else:  # daily or push refresh
        msg = "refreshed"; refresh_stars(st)
        if st["inspect"]: st["inspect"] = repo_info(st["inspect"]["name"]) or st["inspect"]
        save(st); render(st, fetch_events())
    Path(os.environ.get("ARCADE_COMMENT", "/tmp/arcade_comment.md")).write_text(msg + f"\n\n[Back to the arcade](https://github.com/{REPO}#arcade)")
    print(msg)

if __name__ == "__main__": main()
