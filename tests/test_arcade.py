import sys, copy
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import arcade

FAKE = lambda n: {"name": n, "stars": 2, "forks": 0, "issues": 0, "desc": "d", "lang": "Python", "langs": {"Python": 5},
                  "spark": [0]*12, "msg": "m", "date": "2026-10-30", "url": "u"}
def st(): return {"xp": {}, "cheerers": {}, "cheers": {}, "inspect": None, "log": []}

def test_inspect_and_cheer():
    s = st()
    assert arcade.handle(s, "gh|inspect|CognyxOS", "alice", FAKE)[1] and s["inspect"]["name"] == "CognyxOS"
    assert arcade.handle(s, "gh|cheer|kosh", "alice", FAKE)[1] and s["xp"]["kosh"] == 10
    assert not arcade.handle(s, "gh|cheer|kosh", "alice", FAKE)[1]  # once a day

def test_vote_removed_and_rejects():
    s = st()
    for t in ["gh|vote|voice", "gh|vote|mcp", "gh|inspect|notarepo", "gh|cheer|../x", "gh|inspect|CognyxOS; rm -rf /", "", "hi"]:
        before = copy.deepcopy(s)
        assert not arcade.handle(s, t, "bob", FAKE)[1], t
        assert s == before
    assert not arcade.handle(s, "gh|inspect|kosh", "bad user!", FAKE)[1]
    assert not hasattr(arcade, "OPTIONS") and not hasattr(arcade, "raid_svg")

def test_block_has_no_raid_or_log():
    b = arcade.block(st())
    assert "vote" not in b and "raid" not in b.lower() and "ARCADE LOG" not in b
    assert "REPO QUEST" in b and "levelup" not in b and "xp.svg" not in b and "radar.svg" in b

def test_readme_clean():
    md = (Path(arcade.ROOT) / "README.md").read_text()
    for bad in ["SECRET LEVEL", "PATCH NOTES", "KONAMI", "ARCADE LOG", "raid", "vote", "xp.svg", "LEVEL UP"]:
        assert bad not in md, bad
    for good in ["hero-fetch.svg", "quest.svg", "REPO QUEST", "radar.svg", "pacman", "HOW TO PLAY", "footer.svg"]:
        assert good in md, good
