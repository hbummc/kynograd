# Kynograd website

Upload everything in this folder (including the hidden `.nojekyll` file) to the root of a public GitHub repo, e.g. `kynograd`.
Then: repo **Settings → Pages** → Source "Deploy from a branch", branch `main`, folder `/ (root)`.
About a minute later the site is live at `https://<your-name>.github.io/kynograd/`.

## The data files (in `data/`)

| File | What it is |
|---|---|
| `players.json` | Guild and role per resident; `"realtor": true` gives the Housing realtor view |
| `auth.json` | Password hashes, admins, treasurer |
| `housing.json` | The 8 buildings and their apartments (`ready`, `resident`) |
| `bank.json` | The bank: deposits, savings, loans, budget |
| `snapshots.json` / `deposits.json` | Gold balances and last-online times from the EarthMC API |
| `config.json` | Bank rates |

Edit a file on GitHub and the site picks it up within a minute or two.

## Gold tracker

Double-click `start-tracker.bat` to pull the town bank and every resident's gold from EarthMC every 5 minutes. Leave the window open; close it to stop. It needs Python ([python.org](https://www.python.org/downloads/), tick "Add python.exe to PATH").

It writes `data/snapshots.json` and `data/deposits.json` (never `bank.json`). A deposit it can match (town bank up, one resident down by the same amount) is logged under that resident; anything else is logged as unknown for the Treasurer to check. Commit and push `data/` in GitHub Desktop whenever you want the site to show the latest numbers.

One pull by hand: `python scripts/update.py`. Every 10 minutes instead: `python scripts/update.py --watch 10`.

The Treasury desk can't save to GitHub yet (`bankRepo` in `config.json` is empty), so for now bank changes go into `data/bank.json` by hand. That can be switched on later.

Shortcut: hold **Space** and press **S** anywhere for the quick switcher.
