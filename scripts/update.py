#!/usr/bin/env python3
"""Kynograd tracker: pulls the town bank and every resident's gold from the EarthMC API.

    python scripts/update.py            one pull, then stop
    python scripts/update.py --watch    pull every 5 minutes until you close the window
    python scripts/update.py --watch 10 pull every 10 minutes

Or double-click start-tracker.bat in the website folder.

Each pull is compared with the previous snapshot. A new snapshot is saved when any
balance, rank or chunk count changed, or once an hour so last-online times stay fresh.
EarthMC has no deposit history, so deposits are worked out: town bank up and a
resident down by the same amount = that resident deposited. Anything it can't match
is logged with player null ("unknown"), and the Treasurer checks it.

Files it writes (all in data/):
  snapshots.json  balances, last-online times and town info over time
  deposits.json   deposits and withdrawals it could match to a player

It never touches bank.json: that is the Treasurer's official record.
To publish: commit and push data/ in GitHub Desktop.

Test without the network:  python scripts/update.py --offline sample.json
"""
import json, os, sys, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
API = "https://api.earthmc.net/v4"
TOWN = "Kynograd"
TOL = 0.01            # gold rounding tolerance
KEEPALIVE_MIN = 60    # save at least this often, even when nothing changed


def load(name, default):
    try:
        with open(os.path.join(DATA, name), encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save(name, obj):
    """Write to a temp file first, then swap it in, so the site never sees half a file."""
    path = os.path.join(DATA, name)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, path)


def post(path, body):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json",
                                          "User-Agent": "kynograd-tracker"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch():
    town = post("/towns", {"query": [TOWN]})[0]
    names = [r["name"] for r in town["residents"]]
    players = post("/players", {"query": names}) if names else []
    t = int(time.time() * 1000)
    names_of = lambda lst: [x["name"] for x in lst]
    return {
        "t": t,
        "town": round(float(town["stats"]["balance"]), 2),
        "players": {p["name"]: round(float(p["stats"]["balance"]), 2) for p in players},
        "seen": {p["name"]: t if p["status"]["isOnline"] else p["timestamps"]["lastOnline"] for p in players},
        "townInfo": {
            "checked": t,
            "chunks": town["stats"]["numTownBlocks"],
            "maxChunks": town["stats"]["maxTownBlocks"],
            "residents": town["stats"]["numResidents"],
            "nation": (town.get("nation") or {}).get("name"),
            "mayor": town["mayor"]["name"],
            "outlaws": names_of(town["outlaws"]),
            "trusted": names_of(town["trusted"]),
            "ranks": {k: names_of(v) for k, v in sorted(town["ranks"].items())},
        },
    }


def find_subset(items, target):
    """Smallest set of (name, amount) whose amounts add up to target."""
    best = None
    n = min(len(items), 14)
    for mask in range(1, 1 << n):
        pick = [items[i] for i in range(n) if mask >> i & 1]
        if abs(sum(a for _, a in pick) - target) <= TOL and (best is None or len(pick) < len(best)):
            best = pick
    return best


def match(prev, cur):
    """Deposits (+) and withdrawals (-) per player; player None when it can't tell."""
    d_town = round(cur["town"] - prev["town"], 2)
    if abs(d_town) <= TOL:
        return []
    deltas = [(n, round(cur["players"][n] - prev["players"][n], 2))
              for n in cur["players"] if n in prev["players"]]
    if d_town > 0:
        pick = find_subset([(n, -d) for n, d in deltas if d < -TOL], d_town)
        return [{"player": n, "amount": a} for n, a in pick] if pick else [{"player": None, "amount": d_town}]
    pick = find_subset([(n, d) for n, d in deltas if d > TOL], -d_town)
    return [{"player": n, "amount": -a} for n, a in pick] if pick else [{"player": None, "amount": d_town}]


def same(a, b, key):
    return json.dumps(a.get(key), sort_keys=True) == json.dumps(b.get(key), sort_keys=True)


def info_key(s):
    i = dict(s.get("townInfo") or {})
    i.pop("checked", None)
    return json.dumps(i, sort_keys=True)


def step(cur):
    """Compare one pull with the last snapshot, log deposits, save. Returns a one-line summary."""
    cur["town"] = float(cur["town"])
    cur["players"] = {k: float(v) for k, v in cur["players"].items()}
    snaps = load("snapshots.json", [])
    deposits = load("deposits.json", [])
    prev = snaps[-1] if snaps else None

    events = match(prev, cur) if prev else []
    for e in events:
        e["t"] = cur["t"]
    deposits += events

    changed = (prev is None or cur["town"] != prev["town"] or cur["players"] != prev["players"]
               or info_key(cur) != info_key(prev))
    stale = prev is None or cur["t"] - prev["t"] >= KEEPALIVE_MIN * 60_000

    stamp = time.strftime("%H:%M")
    lines = [f"{stamp}  {'deposit' if e['amount'] > 0 else 'withdrawal'}: {e['player'] or 'unknown'} {e['amount']:g}g" for e in events]
    if prev:
        for n, v in cur["players"].items():
            if n in prev["players"] and abs(v - prev["players"][n]) > TOL:
                lines.append(f"{stamp}  {n}: {prev['players'][n]:g}g -> {v:g}g")
        if abs(cur["town"] - prev["town"]) > TOL:
            lines.append(f"{stamp}  town bank: {prev['town']:g}g -> {cur['town']:g}g")
    if changed or stale:
        snaps.append(cur)
        save("snapshots.json", snaps)
        if events:
            save("deposits.json", deposits)
        lines.append(f"{stamp}  saved snapshot #{len(snaps)} · town {cur['town']:g}g")
    else:
        lines.append(f"{stamp}  no change")
    return "\n".join(lines)


def main():
    args = sys.argv[1:]
    if args[:1] == ["--offline"]:
        with open(args[1], encoding="utf-8") as f:
            print(step(json.load(f)))
        return
    if args[:1] == ["--watch"]:
        minutes = float(args[1]) if len(args) > 1 else 5
        print(f"Kynograd tracker: pulling every {minutes:g} min. Close this window to stop.")
        while True:
            try:
                print(step(fetch()), flush=True)
            except Exception as e:  # network hiccup, API down: try again next round
                print(f"{time.strftime('%H:%M')}  pull failed: {e}", flush=True)
            time.sleep(minutes * 60)
    print(step(fetch()))


if __name__ == "__main__":
    main()
