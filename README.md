# Kynograd website

Static site, no build step. Upload everything in this folder to a GitHub repository.

## Put it online with GitHub Pages
1. Create a new repository on GitHub (for example `kynograd`) and upload all files in this folder, keeping the `img` and `icons` folders.
2. In the repository go to **Settings → Pages**, choose **Deploy from a branch**, pick `main` and `/ (root)`, and save.
3. After a minute the site is live at `https://YOUR-NAME.github.io/kynograd/`.

## Turn on the Discord preview
Open `index.html` and replace every `SITE_URL` (4 tags near the top) with your site address, without a slash at the end, for example:

    https://your-name.github.io/kynograd

Commit, wait a minute, then paste the link in Discord: it shows the title, the description and the spawn image (`img/preview.jpg`).

## Pages inside the site
- `#guides` all guides · `#guide-trial` · `#guide-gold` · `#guide-nether`
- `#guildlist` the guilds · `#keyholders` `#builders` `#police` `#resource` guild pages
- `#projects` · `#education` (how joining works)
