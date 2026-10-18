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

The Treasury desk can't save to GitHub yet (`bankRepo` in `config.json` is empty), so for now bank changes go into `data/bank.json` by hand. That can be switched on later.

Shortcut: hold **Space** and press **S** anywhere for the quick switcher.
