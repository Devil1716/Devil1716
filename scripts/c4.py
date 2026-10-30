"""Connect Four played through GitHub issues. Input is only the issue title and author, matched by strict regexes."""
import json, os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "game" / "c4.json"
OUT = ROOT / "assets" / "game"
README = ROOT / "README.md"
REPO = "Devil1716/Devil1716"
ROWS, COLS = 6, 7
MOVE = re.compile(r"^c4\|move\|([1-7])$")
NEW = re.compile(r"^c4\|new$")
USER = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")
F = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Courier New',monospace"
BG, PANEL, PURP, PINK, CYAN, YEL, TXT, DIM, GRN = "#07051a", "#0e0b2b", "#a78bfa", "#ff4fd8", "#22d3ee", "#facc15", "#e2e8f0", "#7c7aa8", "#39d353"
COLOR = {"R": PINK, "Y": YEL}
NAME = {"R": "PINK", "Y": "GOLD"}

def fresh(st=None):
    st = st or {"players": {}, "wins": {"R": 0, "Y": 0, "D": 0}, "games": 0}
    st.update(board=[["."] * COLS for _ in range(ROWS)], turn="R", winner=None, line=[], moves=[])
    return st

def load():
    return json.loads(STATE.read_text()) if STATE.exists() else fresh()

def winline(b, r, c):
    p = b[r][c]
    for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
        cells = [(r, c)]
        for s in (1, -1):
            rr, cc = r + dr * s, c + dc * s
            while 0 <= rr < ROWS and 0 <= cc < COLS and b[rr][cc] == p:
                cells.append((rr, cc)); rr += dr * s; cc += dc * s
        if len(cells) >= 4: return sorted(cells)
    return []

def play(st, title, user):
    """Returns (comment, changed)."""
    title = title.strip()
    if not USER.match(user or ""): return "Unknown player.", False
    if NEW.match(title):
        if st["winner"] is None and st["moves"] and user != "Devil1716": return "A game is still running. Finish it first, then start a new one.", False
        fresh(st); return "New game started. PINK moves first.", True
    m = MOVE.match(title)
    if not m: return "I could not read that move. Use the column links on the profile.", False
    if st["winner"] is not None: return "This game is over. Start a new one with the NEW GAME button.", False
    c = int(m.group(1)) - 1; b = st["board"]
    r = next((r for r in range(ROWS - 1, -1, -1) if b[r][c] == "."), None)
    if r is None: return f"Column {c+1} is full. Pick another one.", False
    p = st["turn"]; b[r][c] = p
    st["moves"].append({"p": p, "col": c + 1, "user": user})
    st["players"][user] = st["players"].get(user, 0) + 1
    line = winline(b, r, c)
    if line:
        st.update(winner=p, line=line); st["wins"][p] += 1; st["games"] += 1
        return f"Four in a row! {NAME[p]} wins, finished by @{user}. Press NEW GAME to play again.", True
    if all(x != "." for x in b[0]):
        st["winner"] = "D"; st["wins"]["D"] += 1; st["games"] += 1
        return "The board is full. It is a draw. Press NEW GAME to play again.", True
    st["turn"] = "Y" if p == "R" else "R"
    return f"{NAME[p]} dropped a disc in column {c+1}. It is now {NAME[st['turn']]}'s turn.", True

def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" shape-rendering="crispEdges">'
            f'<style>text{{font-family:{F}}}</style>{body}</svg>')

def disc(x, y, s, col):  # chunky pixel disc
    q = s // 8; out = []
    for r, row in enumerate(["..####..", ".######.", "########", "########", "########", "########", ".######.", "..####.."]):
        for c, ch in enumerate(row):
            if ch == "#": out.append(f'<rect x="{x+c*q}" y="{y+r*q}" width="{q}" height="{q}" fill="{col}"/>')
    out.append(f'<rect x="{x+2*q}" y="{y+2*q}" width="{q}" height="{q}" fill="#fff" opacity=".55"/>')
    return "".join(out)

def board_svg(st):
    s, g = 64, 12; W = COLS * (s + g) + g + 48; H = ROWS * (s + g) + g + 110
    x0, y0 = 24 + g, 70
    if st["winner"] == "D": status, sc = "DRAW GAME", CYAN
    elif st["winner"]: status, sc = f"{NAME[st['winner']]} WINS", COLOR[st["winner"]]
    else: status, sc = f"{NAME[st['turn']]} TO MOVE", COLOR[st["turn"]]
    b = [f'<rect x="4" y="4" width="{W-8}" height="{H-8}" fill="{BG}" stroke="{CYAN}" stroke-width="4"/>',
         f'<text x="28" y="44" fill="{CYAN}" font-size="18" font-weight="bold" letter-spacing="3">CONNECT FOUR</text>',
         f'<text x="{W-28}" y="44" fill="{sc}" font-size="16" font-weight="bold" text-anchor="end">{status}<animate attributeName="opacity" values="1;.4;1" dur="1.4s" repeatCount="indefinite"/></text>',
         f'<rect x="24" y="{y0-g}" width="{COLS*(s+g)+g}" height="{ROWS*(s+g)+g}" fill="#1b1550" stroke="{PURP}" stroke-width="3"/>']
    win = {tuple(x) for x in st.get("line", [])}
    last = st["moves"][-1] if st["moves"] else None
    for r in range(ROWS):
        for c in range(COLS):
            x, y = x0 + c * (s + g), y0 + r * (s + g); v = st["board"][r][c]
            b.append(disc(x, y, s, PANEL if v == "." else COLOR[v]))
            if (r, c) in win:
                b.append(f'<rect x="{x-3}" y="{y-3}" width="{s+6}" height="{s+6}" fill="none" stroke="#fff" stroke-width="3"><animate attributeName="opacity" values="1;0;1" dur=".8s" repeatCount="indefinite"/></rect>')
    if last and not win:
        c = last["col"] - 1; r = next(r for r in range(ROWS) if st["board"][r][c] != ".")
        b.append(f'<g><animateTransform attributeName="transform" type="translate" values="0 {-(r+1)*(s+g)};0 0" dur=".5s" fill="freeze"/>{disc(x0+c*(s+g), y0+r*(s+g), s, COLOR[last["p"]])}</g>')
    w = st["wins"]
    b.append(f'<text x="28" y="{H-22}" fill="{DIM}" font-size="13">PINK {w["R"]}  ·  GOLD {w["Y"]}  ·  DRAWS {w["D"]}  ·  MOVES {len(st["moves"])}</text>')
    return svg(W, H, "".join(b))

def button_svg(label, color, w=72):
    return svg(w, 44, f'<rect x="2" y="2" width="{w-4}" height="40" fill="{PANEL}" stroke="{color}" stroke-width="3"/>'
                      f'<text x="{w/2}" y="29" fill="{color}" font-size="18" font-weight="bold" text-anchor="middle">{label}</text>')

def readme_block(st):
    url = f"https://github.com/{REPO}/issues/new?title=c4%7Cmove%7C{{n}}&body=Just+press+Submit+new+issue.+The+arcade+bot+plays+your+move."
    cols = " ".join(f'<a href="{url.format(n=n)}"><img src="./assets/game/col-{n}.svg" width="8.6%" alt="Drop in column {n}" /></a>' for n in range(1, 8))
    new = f'<a href="https://github.com/{REPO}/issues/new?title=c4%7Cnew&body=Just+press+Submit+new+issue."><img src="./assets/game/new.svg" height="40" alt="New game" /></a>'
    recent = "".join(f"<tr><td>{NAME[m['p']]}</td><td>column {m['col']}</td><td><a href=\"https://github.com/{m['user']}\">@{m['user']}</a></td></tr>" for m in reversed(st["moves"][-5:])) or "<tr><td colspan=\"3\">No moves yet. Be the first.</td></tr>"
    top = sorted(st["players"].items(), key=lambda x: -x[1])[:5]
    tops = "".join(f"<tr><td>{i+1}</td><td><a href=\"https://github.com/{u}\">@{u}</a></td><td>{n}</td></tr>" for i, (u, n) in enumerate(top)) or "<tr><td colspan=\"3\">Leaderboard is empty.</td></tr>"
    turn = "Game over. " if st["winner"] else f"It is <b>{NAME[st['turn']]}</b>'s turn. "
    return (f'<!--C4:START-->\n<a id="arcade"></a>\n{cols}\n\n<img src="./assets/game/board.svg" width="70%" alt="Connect Four board" />\n\n'
            f'{turn}Click a column above, then press Submit. {new}\n\n'
            f'<details><summary><b>LAST MOVES and HIGH SCORES</b></summary>\n\n<table><tr><th>Disc</th><th>Move</th><th>Player</th></tr>{recent}</table>\n\n'
            f'<table><tr><th>#</th><th>Player</th><th>Moves</th></tr>{tops}</table>\n</details>\n<!--C4:END-->')

def render(st):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "board.svg").write_text(board_svg(st))
    for n in range(1, 8): (OUT / f"col-{n}.svg").write_text(button_svg(f"▼{n}", COLOR[st["turn"]] if not st["winner"] else DIM))
    (OUT / "new.svg").write_text(button_svg("NEW GAME", GRN, 150))
    md = README.read_text()
    md = re.sub(r"<!--C4:START-->.*?<!--C4:END-->", lambda _: readme_block(st), md, flags=re.S)
    README.write_text(md)

def main():
    title, user = os.environ.get("ISSUE_TITLE", ""), os.environ.get("ISSUE_USER", "")
    st = load()
    msg, changed = play(st, title, user) if title else ("", True)
    if changed:
        STATE.parent.mkdir(exist_ok=True); STATE.write_text(json.dumps(st))
        render(st)
    Path(os.environ.get("C4_COMMENT", "/tmp/c4_comment.md")).write_text(msg + f"\n\n[Back to the arcade](https://github.com/{REPO}#arcade)")
    print(msg)

if __name__ == "__main__": main()
