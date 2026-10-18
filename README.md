# Kynograd website

Static site, no build step, no bots. Upload everything in this folder to a GitHub repository.

## Put it online with GitHub Pages
1. Create a new repository on GitHub (for example `kynograd`) and upload all files in this folder, keeping the folders.
2. In the repository go to **Settings → Pages**, choose **Deploy from a branch**, pick `main` and `/ (root)`, and save.
3. After a minute the site is live at `https://YOUR-NAME.github.io/kynograd/`.

## Discord preview
Open `index.html` and replace every `SITE_URL` (4 tags near the top) with your site address, without a slash at the end, for example `https://your-name.github.io/kynograd`.

## Pages inside the site
- `#guides` all guides · `#guide-trial` · `#guide-gold` · `#guide-nether`
- `#guildlist` the guilds · `#keyholders` `#builders` `#police` `#resource` guild pages
- `#projects` · `#education` (how joining works)
- Member area (click the flag in the header to sign in): `#members`, `#player-NAME`, `#admin` (Bank stats, for the Treasurer and Mayor), `#bank-policy` (public)

## Updating the bank (about twice a day)
1. Run the update script from this folder:

       python scripts/update.py

   It reads the town and every resident's balance from EarthMC, compares with the last time,
   and adds any gold deposits (100 roubles per 1g) to `data/deposits.json` and `data/snapshots.json`.
   (Or just say "run" to Claude, who does the same and gives you the two files.)
2. Upload the changed files in `data/` to GitHub.

## How the bank works
Residents fill in a short form on their bank page, copy the message and paste it in #town-bank
to ask the Treasurer (GarrisonGrim) to send roubles, move savings, cash out or take a loan.
The Treasurer does it in-game; when you update, add it to `data/bank.json`
(or tell Claude what happened and get the updated file back):
- `transfers` roubles sent between residents: {"t", "from", "to", "roubles", "note"}
- `savings` into (+) or out of (-) savings: {"t", "player", "roubles", "fee"}
- `cashouts` roubles cashed out as gold: {"t", "player", "roubles", "gold", "status": "paid"}
- `spending` roubles spent with the town: {"t", "player", "roubles", "note"}
- `loans` gold loans (30 days each): {"id", "player", "gold", "days", "accepted", "repaid": [{"t", "gold"}], "status"}
`t` is the time in milliseconds. Interest, fees and late penalties are worked out by the page.

## Data files
- `data/bank.json` the bank's records (lines from the Treasury desk)
- `data/players.json` guilds, roles and project history
- `data/auth.json` password hashes; `admins` get the Treasury desk; `treasurer` names the Treasurer
- `data/config.json` rates (roublesPerGold, savingsRate, loanRate, lateDaily, earlyFee, lockDays,
  defaultAfter, loanDays, noticeShare, maxWorkdays) and `repo`: your repo address, e.g.
  `https://github.com/your-name/kynograd`, so the Treasury desk links straight to each file.
- `data/snapshots.json`, `data/deposits.json` written by the update script

The sign-in is a soft lock: it keeps casual visitors out, but the data files are public.
Never upload the passwords list; only the hashes in `auth.json` belong in the repo.
