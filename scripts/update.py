#!/usr/bin/env python3
"""Kynograd bank update. Run it by hand whenever you want (e.g. twice a day):

    python scripts/update.py          (from the website folder)

EarthMC has no deposit history, so this takes a snapshot of the town bank and
every resident's balance, compares it with the previous snapshot and works out
who deposited (town bank up, a resident down by the same amount). Then upload
data/snapshots.json and data/deposits.json to GitHub (or commit and push).

Files it writes (all in data/):
  snapshots.json  every change in balances over time
  deposits.json   every deposit and withdrawal it could match to a player

Deposits earn roubles: ROUBLES_PER_GOLD per 1 gold (see data/config.json).
Matching is a best guess: the longer between runs, the more likely a deposit
and a shop purchase get mixed up. Unmatched changes land as "unknown".

Test without the network:  python3 scripts/track.py --offline sample.json
"""
import json, os, sys, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
API = "https://api.earthmc.net/v4"
TOWN = "Kynograd"
TOL = 0.01          # gold rounding tolerance
KEEPALIVE_H = 0     # by hand: always save a snapshot


def load(name, default):
    try:
        with open(os.path.join(DATA, name), encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save(name, obj):
    with open(os.path.join(DATA, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")


def post(path, body):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json",
                                          "User-Agent": "kynograd-update"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch():
    town = post("/towns", {"query": [TOWN]})[0]
    names = [r["name"] for r in town["residents"]]
    players = post("/players", {"query": names}) if names else []
    return {
        "t": int(time.time() * 1000),
        "town": round(float(town["stats"]["balance"]), 2),
        "players": {p["name"]: round(float(p["stats"]["balance"]), 2) for p in players},
    }


def find_subset(items, target):
    """Smallest set of (name, amount) whose amounts add up to target."""
    best = None
    n = len(items)
    for mask in range(1, 1 << min(n, 14)):
        pick = [items[i] for i in range(min(n, 14)) if mask >> i & 1]
        if abs(sum(a for _, a in pick) - target) <= TOL and (best is None or len(pick) < len(best)):
            best = pick
    return best


def match(prev, cur):
    """Return events: deposits (+) and withdrawals (-) per player, or 'unknown'."""
    events = []
    d_town = round(cur["town"] - prev["town"], 2)
    if abs(d_town) <= TOL:
        return events
    # only residents present in both snapshots can be matched
    deltas = [(n, round(cur["players"][n] - prev["players"][n], 2))
              for n in cur["players"] if n in prev["players"]]
    if d_town > 0:
        losers = [(n, -d) for n, d in deltas if d < -TOL]
        pick = find_subset(losers, d_town)
        if pick:
            events += [{"player": n, "amount": a} for n, a in pick]
        else:
            events.append({"player": None, "amount": d_town})
    else:
        gainers = [(n, d) for n, d in deltas if d > TOL]
        pick = find_subset(gainers, -d_town)
        if pick:
            events += [{"player": n, "amount": -a} for n, a in pick]
        else:
            events.append({"player": None, "amount": d_town})
    return events


def main():
    if len(sys.argv) > 2 and sys.argv[1] == "--offline":
        with open(sys.argv[2], encoding="utf-8") as f:
            cur = json.load(f)
    else:
        cur = fetch()

    snaps = load("snapshots.json", [])
    deposits = load("deposits.json", [])
    prev = snaps[-1] if snaps else None

    changed = prev is None or cur["town"] != prev["town"] or cur["players"] != prev["players"]
    stale = prev is None or cur["t"] - prev["t"] > KEEPALIVE_H * 3600_000

    if prev:
        for e in match(prev, cur):
            e["t"] = cur["t"]
            deposits.append(e)
            who = e["player"] or "unknown"
            print(f"{'deposit' if e['amount'] > 0 else 'withdrawal'}: {who} {e['amount']}g")

    if changed or stale:
        snaps.append(cur)
        save("snapshots.json", snaps)
        save("deposits.json", deposits)
        print(f"snapshot saved: town {cur['town']}g, {len(cur['players'])} residents")
    else:
        print("no change")


if __name__ == "__main__":
    main()
