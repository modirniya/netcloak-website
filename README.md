# netcloak.app

The marketing site for NetCloak, a free WireGuard® VPN for Android by NeuEra Apps.
Static HTML on GitHub Pages, served from `main` at the repository root, custom domain
`netcloak.app` (see `CNAME`). No framework, no analytics, no third-party requests.

## Layout

```
site/build.py        the generator (Python 3.10+, standard library)
site/content.py      every word the site says, and the constants the build needs
site/legal_cache/    the mirrored Privacy Policy and Terms of Use, committed
assets/site.css      generated stylesheet
assets/fonts/        IBM Plex Sans (variable) and IBM Plex Mono, latin subsets, OFL
assets/img/          app icon at every size, Open Graph cards, the Google Play badge
index.html, download/, privacy/, terms/, 404.html    generated pages
robots.txt, sitemap.xml, site.webmanifest            generated
```

Edit `site/content.py` or `site/build.py`. Never edit the generated files; the build
overwrites them and `--check` will flag the drift.

## Build

```
python3 site/build.py               # write every page and asset
python3 site/build.py --check       # exit 1 and list what would change; nothing is written
python3 site/build.py --sync-legal  # refresh the legal mirrors from legal.neuera.app, then build
python3 site/build.py --ping        # after a deploy, tell IndexNow the sitemap changed
```

Optional inputs, both read only at build time and never committed:

- `PLAY_SA_KEY` — path to a Google service-account JSON key with access to the app in
  Play Console. When set, the build confirms the current production version name and
  code from the Play Developer API for `/download/`. When unset, the cached values in
  `content.py` are used and a note is printed. The API carries no release date, so
  `APP_RELEASE_DATE` in `content.py` is moved forward by hand when a build ships.
- `PLEX_TTF_DIR` — a folder holding `IBMPlexSans-Regular.ttf`, `IBMPlexSans-SemiBold.ttf`
  and `IBMPlexMono-Medium.ttf`, used only to draw the Open Graph images with PIL.
  Defaults to `../plex-ttf` next to the repository. Without it PIL's default font is
  used and a warning printed; without PIL the existing images are kept.

## Deploy

A push to `main` is a deploy. GitHub Pages serves the committed output; there is no
build server. Run `--check` before committing so the tree and the source agree.

## Legal documents

`/privacy/` and `/terms/` are copies of the documents published at
https://legal.neuera.app/netcloak/, which is their canonical home and keeps every past
version. The copies carry `rel=canonical` pointing there and are excluded from the
sitemap. Run `--sync-legal` whenever a policy is republished.

## Trademarks

"WireGuard" and the "WireGuard" logo are registered trademarks of Jason A. Donenfeld.
The site uses the name descriptively and never shows the logo. Google Play and the
Google Play logo are trademarks of Google LLC; the badge in `assets/img/` is the
official artwork and must stay unmodified.

## Adding a page

Add an entry to `PAGES` in `site/content.py` (title, description, eyebrow, h1, lede, an
`og` tuple for the share card, a `nav` slot or `None` for footer-only, and a list of
blocks). The build renders it, adds a breadcrumb and BreadcrumbList schema, draws its
Open Graph card, and lists it in the sitemap. Header nav order is `NAV_ORDER`.
`/faq/` is driven by `FAQ_ITEMS`; its visible text and its FAQPage schema come from the
same list, so they cannot drift apart.

## CI

`.github/workflows/lighthouse.yml` runs `site/build.py --check` and Lighthouse CI against
`/`, `/no-account/` and `/faq/` on every push and pull request, asserting 0.95 or better
on performance, accessibility, best practices and SEO.
