#!/usr/bin/env python3
"""Generate netcloak.app.

    python3 site/build.py               # write every page and asset
    python3 site/build.py --check       # report what would change, write nothing (exit 1 if stale)
    python3 site/build.py --sync-legal  # refresh the mirrored legal documents, then build
    python3 site/build.py --ping        # after a deploy: tell IndexNow the sitemap changed

Output lands in the repository root, which is what GitHub Pages serves. Source is this file plus
site/content.py. Standard library only; PIL is used if present to draw the Open Graph images and
icons, and pyjwt only when PLAY_SA_KEY points at a service-account key, to ask the Play Developer
API for the current version. Neither is required for an ordinary build.
"""

from __future__ import annotations

import datetime
import html
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import content as C  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CHECK = "--check" in sys.argv
_changed: list[str] = []
PAGES: list[dict] = []   # every indexable page, in the order it was built
NAV: list[tuple[str, str]] = []  # derived from the pages that exist; see nav_page()


def write(rel: str, text: str) -> None:
    path = ROOT / rel
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return
    _changed.append(rel)
    if not CHECK:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def write_bytes(rel: str, data: bytes) -> None:
    path = ROOT / rel
    if path.exists() and path.read_bytes() == data:
        return
    _changed.append(rel)
    if not CHECK:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def e(s: str) -> str:
    return html.escape(s, quote=True)


def nav_page(path: str, label: str) -> None:
    """Register a page in the header nav. Only pages that are built get a link, so a later
    pass adds navigation by adding a page, never by editing a list that can go stale."""
    if (path, label) not in NAV:
        NAV.append((path, label))


# ==================================================================================================
# Live values: the app version from the Play Developer API
# ==================================================================================================

def app_version() -> tuple[str, int, str]:
    """(version name, version code, release date).

    Refreshed from the Play Developer API when PLAY_SA_KEY names a service-account key. The key
    is read only to sign a token and is never copied anywhere. The API carries no release date,
    so the date comes from content.py; if the API reports a newer version code than the cached
    one, the build date is used and a warning printed so content.py gets updated.
    """
    name, code, date = C.APP_VERSION_NAME, C.APP_VERSION_CODE, C.APP_RELEASE_DATE
    key = os.environ.get("PLAY_SA_KEY")
    if not key or not os.path.exists(key):
        print(f"  app version: PLAY_SA_KEY not set, using cached {name} ({code})")
        return name, code, date
    try:
        import time
        import urllib.parse
        import urllib.request

        import jwt  # pyjwt

        sa = json.load(open(key))
        now = int(time.time())
        assertion = jwt.encode(
            {"iss": sa["client_email"],
             "scope": "https://www.googleapis.com/auth/androidpublisher",
             "aud": "https://oauth2.googleapis.com/token", "iat": now, "exp": now + 600},
            sa["private_key"], algorithm="RS256")
        body = urllib.parse.urlencode({
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": assertion}).encode()
        tok = json.load(urllib.request.urlopen(urllib.request.Request(
            "https://oauth2.googleapis.com/token", data=body), timeout=30))["access_token"]
        base = ("https://androidpublisher.googleapis.com/androidpublisher/v3/applications/"
                f"{C.PACKAGE}")
        hdr = {"Authorization": f"Bearer {tok}", "Content-Type": "application/json"}
        edit = json.load(urllib.request.urlopen(urllib.request.Request(
            f"{base}/edits", data=b"{}", headers=hdr, method="POST"), timeout=30))
        try:
            track = json.load(urllib.request.urlopen(urllib.request.Request(
                f"{base}/edits/{edit['id']}/tracks/production", headers=hdr), timeout=30))
        finally:
            urllib.request.urlopen(urllib.request.Request(
                f"{base}/edits/{edit['id']}", headers=hdr, method="DELETE"), timeout=30)
        live = [r for r in track.get("releases", []) if r.get("status") == "completed"]
        if not live:
            print("  app version: no completed production release, using cached values")
            return name, code, date
        rel = live[0]
        api_code = int(max(rel["versionCodes"], key=int))
        api_name = rel.get("name", "").split(" ")[-1].strip("()") or name
        if api_code != code:
            date = datetime.date.today().isoformat()
            print(f"  app version: API reports {api_name} ({api_code}); cached content.py has "
                  f"{name} ({code}). Using today as the release date — update content.py.")
        else:
            print(f"  app version: {api_name} ({api_code}) confirmed by the Play API")
        return api_name, api_code, date
    except Exception as ex:  # a build must never fail because Google was slow
        print(f"  app version: API unavailable ({ex.__class__.__name__}), using cached {name}")
        return name, code, date


VERSION_NAME, VERSION_CODE, RELEASE_DATE = C.APP_VERSION_NAME, C.APP_VERSION_CODE, C.APP_RELEASE_DATE


# ==================================================================================================
# Layout
# ==================================================================================================

def ld_org() -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "@id": f"{C.SITE}/#organization",
        "name": C.ORG["name"],
        "legalName": C.ORG["legalName"],
        "email": C.ORG["email"],
        "url": C.ORG["url"],
        "logo": f"{C.SITE}/assets/img/icon-512.png",
    }


def ld_website() -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "@id": f"{C.SITE}/#website",
        "url": C.SITE + "/",
        "name": f"{C.NAME} VPN",
        "publisher": {"@id": f"{C.SITE}/#organization"},
    }


def ld_app() -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "MobileApplication",
        "name": C.NAME,
        "operatingSystem": "Android",
        "applicationCategory": "SecurityApplication",
        "softwareVersion": VERSION_NAME,
        "installUrl": C.PLAY,
        "url": C.SITE + "/",
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "author": {"@id": f"{C.SITE}/#organization"},
        "image": f"{C.SITE}/assets/img/icon-512.png",
    }


def layout(*, path: str, title: str, description: str, body: str,
           ld: list[dict] | None = None, og: str = "og-home.png",
           canonical: str | None = None, nav_current: str = "",
           in_sitemap: bool = True, extra_head: str = "") -> str:
    url = C.SITE + path
    canon = canonical or url
    blocks = [ld_org(), ld_website()] + list(ld or [])
    ld_tags = "".join(
        f'<script type="application/ld+json">{json.dumps(b, ensure_ascii=False)}</script>'
        for b in blocks)
    nav_links = "".join(
        '<a href="{}"{}>{}</a>'.format(
            e(u), ' aria-current="page"' if u == nav_current else "", e(t))
        for u, t in NAV)
    verify = (f'<meta name="google-site-verification" content="{e(C.SEARCH_CONSOLE_META_CONTENT)}">\n'
              if C.SEARCH_CONSOLE_META_CONTENT else "")
    if in_sitemap:
        PAGES.append({"path": path})
    year = datetime.date.today().year

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{e(canon)}">
<meta name="robots" content="index,follow,max-image-preview:large">
{verify}<meta name="theme-color" media="(prefers-color-scheme: dark)" content="#0B1210">
<meta name="theme-color" media="(prefers-color-scheme: light)" content="#F4F7F4">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/img/favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/assets/img/favicon-16.png">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{e(C.NAME)} VPN">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{e(canon)}">
<meta property="og:image" content="{C.SITE}/assets/img/{og}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(C.NAME)}: {e(C.TAGLINE)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(description)}">
<meta name="twitter:image" content="{C.SITE}/assets/img/{og}">
<link rel="preload" href="/assets/fonts/IBMPlexSans-Variable.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/IBMPlexMono-500.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/site.css">
{extra_head}{ld_tags}</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-head">
  <div class="bar">
    <a class="brand" href="/" aria-label="{e(C.NAME)} home">
      <img src="/assets/img/icon-64.png" alt="" width="32" height="32">
      <span>{e(C.NAME)}</span>
    </a>
    <nav class="site-nav" aria-label="Main">{nav_links}</nav>
    <a class="btn btn-primary btn-sm" href="{C.PLAY}">Get the app</a>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-foot">
  <div class="foot-grid">
    <div>
      <p class="foot-brand">{e(C.NAME)}</p>
      <p class="foot-note">Free WireGuard® VPN for Android. No account, timed sessions,
      one server in New York, and a plain statement of what we keep.</p>
      <a class="badge-link" href="{C.PLAY}"><img src="/assets/img/google-play-badge.png"
        alt="Get it on Google Play" width="162" height="63"></a>
    </div>
    <div>
      <p class="foot-h">Product</p>
      <a href="/">Home</a>
      <a href="/download/">Download</a>
      <a href="{C.PLAY}">Google Play listing</a>
    </div>
    <div>
      <p class="foot-h">Legal</p>
      <a href="/privacy/">Privacy Policy</a>
      <a href="/terms/">Terms of Use</a>
      <a href="{C.LEGAL_HUB}">Version history</a>
    </div>
    <div>
      <p class="foot-h">Company</p>
      <a href="{C.ORG['url']}">{e(C.ORG['name'])}</a>
      <a href="mailto:{C.ORG['email']}">{C.ORG['email']}</a>
    </div>
  </div>
  <p class="fineprint">© {year} {e(C.ORG['legalName'])} · {e(C.NAME)} is a product of {e(C.ORG['name'])}.
  {e(C.WIREGUARD_ATTRIBUTION)} {e(C.PLAY_ATTRIBUTION)}</p>
</footer>
</body>
</html>
"""


# ==================================================================================================
# Stylesheet — dark-first, every colour through a token
# ==================================================================================================

CSS = """/* Generated by site/build.py — do not edit. */
@font-face{font-family:"IBM Plex Sans";font-style:normal;font-weight:100 700;font-display:swap;
  src:url(/assets/fonts/IBMPlexSans-Variable.woff2) format("woff2")}
@font-face{font-family:"IBM Plex Mono";font-style:normal;font-weight:400;font-display:swap;
  src:url(/assets/fonts/IBMPlexMono-400.woff2) format("woff2")}
@font-face{font-family:"IBM Plex Mono";font-style:normal;font-weight:500;font-display:swap;
  src:url(/assets/fonts/IBMPlexMono-500.woff2) format("woff2")}

:root{
  --ground:#0B1210; --raised:#111A16; --sunken:#0F1613;
  --ink:#EAF2EC; --ink-2:#B7C4BC; --ink-3:#8A9890;
  --line:rgba(234,242,236,.12); --line-strong:rgba(234,242,236,.24);
  --accent:#1EC860; --accent-ink:#5FE08F; --accent-soft:rgba(30,200,96,.14);
  --on-accent:#06140B;
  --marathon:#4A90E2; --balanced:#B07CD6; --sprint:#F39C12;
  --sans:"IBM Plex Sans",-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  --measure:68ch; --wrap:1080px; --pad:clamp(16px,4vw,28px);
  --ease:cubic-bezier(.2,0,0,1);
  color-scheme:dark;
}
@media (prefers-color-scheme:light){
  :root:not([data-theme="dark"]){
    --ground:#F4F7F4; --raised:#FFFFFF; --sunken:#E9EFEA;
    --ink:#0E1512; --ink-2:#3E4944; --ink-3:#6F7B74;
    --line:rgba(14,21,18,.12); --line-strong:rgba(14,21,18,.22);
    --accent:#128A45; --accent-ink:#0E6E37; --accent-soft:#DDF3E5;
    --on-accent:#FFFFFF;
    --marathon:#2F6FC4; --balanced:#7E43A8; --sprint:#C77A0C;
    color-scheme:light;
  }
}
:root[data-theme="light"]{
  --ground:#F4F7F4; --raised:#FFFFFF; --sunken:#E9EFEA;
  --ink:#0E1512; --ink-2:#3E4944; --ink-3:#6F7B74;
  --line:rgba(14,21,18,.12); --line-strong:rgba(14,21,18,.22);
  --accent:#128A45; --accent-ink:#0E6E37; --accent-soft:#DDF3E5;
  --on-accent:#FFFFFF;
  --marathon:#2F6FC4; --balanced:#7E43A8; --sprint:#C77A0C;
  color-scheme:light;
}

*{box-sizing:border-box}
html{scroll-behavior:smooth}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{animation:none!important;transition:none!important}}
body{margin:0;background:var(--ground);color:var(--ink);font:16px/1.6 var(--sans);
  padding-inline:var(--pad);-webkit-font-smoothing:antialiased;font-variant-numeric:tabular-nums}
a{color:var(--accent-ink);text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:3px}
a:hover{text-decoration-thickness:2px}
:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:3px}
img{max-width:100%;height:auto}
h1,h2,h3{text-wrap:balance;line-height:1.12;margin:0;letter-spacing:-.02em;font-weight:600}
h1{font-size:clamp(32px,5vw,50px)}
h2{font-size:clamp(24px,3.2vw,32px)}
h3{font-size:18px;letter-spacing:-.01em}
p{margin:0}
.wrap{max-width:var(--wrap);margin-inline:auto}
.prose{max-width:var(--measure)}
.eyebrow{font:500 12px/1 var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--accent-ink);margin:0 0 12px}
.lede{font-size:18px;color:var(--ink-2);max-width:var(--measure)}
.skip{position:absolute;left:-9999px;top:0;background:var(--accent);color:var(--on-accent);padding:10px 16px;z-index:20;text-decoration:none}
.skip:focus{left:8px;top:8px}

/* header */
.site-head{position:sticky;top:0;z-index:10;background:color-mix(in srgb,var(--ground) 86%,transparent);
  backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);border-bottom:1px solid var(--line);margin-inline:calc(-1 * var(--pad));padding-inline:var(--pad)}
.bar{max-width:var(--wrap);margin-inline:auto;height:64px;display:flex;align-items:center;gap:20px}
.brand{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--ink);font-weight:600;font-size:17px;letter-spacing:-.01em}
.brand img{border-radius:8px}
.site-nav{display:flex;gap:18px;margin-left:auto;font-size:15px}
.site-nav a{color:var(--ink-2);text-decoration:none}
.site-nav a:hover,.site-nav a[aria-current]{color:var(--ink)}

/* buttons */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;padding:12px 18px;border-radius:9px;font-weight:600;text-decoration:none;font-size:15px;transition:transform .18s var(--ease),background .18s var(--ease)}
.btn-primary{background:var(--accent);color:var(--on-accent)}
.btn-primary:hover{transform:translateY(-1px)}
.btn-ghost{border:1px solid var(--line-strong);color:var(--ink)}
.btn-sm{padding:8px 13px;font-size:14px;flex-shrink:0}
.badge-link{display:inline-block;line-height:0}

/* sections */
section{max-width:var(--wrap);margin-inline:auto;padding-block:56px;border-bottom:1px solid var(--line)}
section:last-of-type{border-bottom:0}
.hero{display:grid;grid-template-columns:1.15fr 1fr;gap:40px;align-items:center;padding-block:56px 64px}
.hero .sub{margin-top:16px}
.hero .actions{margin-top:22px;display:flex;flex-wrap:wrap;gap:12px;align-items:center}
.small{font-size:13px;color:var(--ink-3);margin-top:14px}

/* the session card, as the app draws it */
.card{background:var(--raised);border:1px solid var(--line);border-radius:16px;padding:22px;display:grid;gap:14px;font-family:var(--mono);box-shadow:0 20px 60px -30px rgba(0,0,0,.5)}
.card .st{display:flex;justify-content:space-between;align-items:center;font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-3)}
.card .st b{color:var(--accent-ink);font-weight:500}
.card .time{font-size:clamp(48px,8vw,64px);line-height:1;font-weight:500;letter-spacing:-.03em}
.card .bar{height:8px;border-radius:999px;background:var(--line);overflow:hidden}
.card .bar i{display:block;height:100%;width:100%;background:var(--balanced);border-radius:999px;transition:width 1s linear}
.modes{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.mode{border:1px solid var(--line);border-radius:10px;padding:10px 11px;display:grid;gap:3px;font-size:12px;color:var(--ink-2)}
.mode b{font-weight:500;color:var(--ink)}
.mode.on{box-shadow:inset 0 0 0 2px var(--balanced)}
.mode.marathon b{color:var(--marathon)} .mode.balanced b{color:var(--balanced)} .mode.sprint b{color:var(--sprint)}

/* content blocks */
.grid{display:grid;gap:16px;margin-top:24px}
.grid.three{grid-template-columns:repeat(auto-fit,minmax(240px,1fr))}
.panel{background:var(--raised);border:1px solid var(--line);border-radius:12px;padding:18px 20px;display:grid;gap:8px;align-content:start}
.panel h3{font-size:16px}
.panel p{color:var(--ink-2);font-size:15px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin-top:24px}
.tile{border:1px solid var(--line);border-radius:12px;padding:18px;display:grid;gap:6px;background:var(--raised)}
.tile .n{font:500 32px/1 var(--mono);letter-spacing:-.02em}
.tile .n small{font-size:14px;color:var(--ink-3);margin-left:6px;letter-spacing:0}
.tile .x{font:500 12px/1 var(--mono);letter-spacing:.08em;text-transform:uppercase}
.tile.marathon .x,.tile.marathon .n{color:var(--marathon)}
.tile.balanced .x,.tile.balanced .n{color:var(--balanced)}
.tile.sprint .x,.tile.sprint .n{color:var(--sprint)}
.tile p{color:var(--ink-2);font-size:14px}
.stack{display:grid;gap:14px;margin-top:20px;max-width:var(--measure)}
.stack p{color:var(--ink-2)}
.keep{margin-top:22px;max-width:var(--measure);border-left:3px solid var(--accent);background:var(--accent-soft);padding:16px 20px;border-radius:0 10px 10px 0;font-size:17px;line-height:1.65}
.after{margin-top:14px;color:var(--ink-2);max-width:var(--measure)}

/* faq */
.faq{display:grid;gap:0;margin-top:20px;max-width:var(--measure);border-top:1px solid var(--line)}
.faq details{border-bottom:1px solid var(--line)}
.faq summary{cursor:pointer;padding:16px 0;font-weight:500;list-style:none;display:flex;justify-content:space-between;gap:16px;align-items:center}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"+";font:500 20px/1 var(--mono);color:var(--ink-3);flex-shrink:0}
.faq details[open] summary::after{content:"–"}
.faq details p{color:var(--ink-2);padding:0 0 18px;max-width:var(--measure)}

/* install */
.install{display:flex;flex-wrap:wrap;gap:24px;align-items:center;margin-top:20px}
.install p{color:var(--ink-2)}

/* download page */
.facts{display:grid;grid-template-columns:max-content 1fr;gap:10px 22px;margin:22px 0 0;font-size:15px;max-width:var(--measure)}
.facts dt{color:var(--ink-3);font:500 13px/1.6 var(--mono)}
.facts dd{margin:0}

/* legal mirror */
.legal{max-width:var(--measure)}
.legal .notice{background:var(--raised);border:1px solid var(--line);border-radius:10px;padding:12px 16px;font-size:14px;color:var(--ink-2);margin-bottom:28px}
.legal h1,.legal h2,.legal h3{margin-top:1.4em;margin-bottom:.5em}
.legal p,.legal li{color:var(--ink-2)}
.legal ul,.legal ol{padding-left:22px}
.legal .version-banner,.legal .document-header,.legal .doc-actions{display:none}
.legal table{border-collapse:collapse;width:100%;font-size:14px}
.legal td,.legal th{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}

/* footer */
.site-foot{max-width:var(--wrap);margin:24px auto 0;padding-block:40px 32px;border-top:1px solid var(--line)}
.foot-grid{display:grid;grid-template-columns:1.6fr 1fr 1fr 1fr;gap:28px}
.foot-grid a{display:block;color:var(--ink-2);text-decoration:none;font-size:15px;margin-top:8px}
.foot-grid a:hover{color:var(--ink);text-decoration:underline}
.foot-brand{font-weight:600;font-size:17px}
.foot-note{color:var(--ink-2);font-size:14px;margin:8px 0 14px;max-width:38ch}
.foot-h{font:500 12px/1 var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3)}
.fineprint{margin-top:32px;font-size:12px;color:var(--ink-3);max-width:80ch;line-height:1.6}

@media (max-width:820px){
  .hero{grid-template-columns:1fr;gap:28px}
  .foot-grid{grid-template-columns:1fr 1fr}
  .site-nav{display:none}
}
@media (max-width:480px){
  .foot-grid{grid-template-columns:1fr}
  .facts{grid-template-columns:1fr;gap:2px}
  .facts dt{margin-top:10px}
  .modes{grid-template-columns:1fr}
}
"""

# The card counts down from 40:00 once the page is visible and stops at 39:00, so it reads as a
# clock and never as a broken one. Nothing runs under reduced motion; the page shows 40:00 at rest.
COUNTDOWN_JS = """<script>
(function(){
  if(matchMedia("(prefers-reduced-motion: reduce)").matches)return;
  var t=document.getElementById("t"),b=document.getElementById("b"),s=2400,end=2340,id;
  function tick(){
    if(document.hidden)return;
    s-=1;
    t.textContent=(""+Math.floor(s/60)).padStart(2,"0")+":"+(""+s%60).padStart(2,"0");
    b.style.width=(s/2400*100)+"%";
    if(s<=end)clearInterval(id);
  }
  id=setInterval(tick,1000);
})();
</script>"""


# ==================================================================================================
# Pages
# ==================================================================================================

def session_card() -> str:
    tiles = "".join(
        f'<div class="mode {k}{" on" if k == C.DEFAULT_MODE else ""}"><b>{e(n)}</b>'
        f'<span>{m} min · {x}</span></div>'
        for k, n, m, x, _ in C.MODES)
    return f"""<div class="card" role="img" aria-label="The app's session card: protected, New York, 40 minutes left in Balanced mode">
  <div class="st"><span>Protected</span><b>New York, US</b></div>
  <div class="time" id="t">40:00</div>
  <div class="bar"><i id="b"></i></div>
  <div class="modes">{tiles}</div>
</div>"""


def build_home() -> None:
    nav_page("/", "Home")
    H = C.HERO
    tiles = "".join(
        f'<div class="tile {k}"><span class="x">{e(n)}</span>'
        f'<span class="n">{m}<small>min</small></span><span class="x">{x} speed</span>'
        f'<p>{e(u)}</p></div>'
        for k, n, m, x, u in C.MODES)
    protects = "".join(
        f"<div class=\"panel\"><h3>{e(h)}</h3><p>{e(p)}</p></div>"
        for h, p in C.PROTECTS["items"])
    faq = "".join(
        f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>"
        for q, a in C.HOME_FAQ)
    body = f"""
<section class="hero">
  <div>
    <p class="eyebrow">{e(H['eyebrow'])}</p>
    <h1>{e(H['h1'])}</h1>
    <p class="lede sub">{e(H['sub'])}</p>
    <div class="actions">
      <a class="btn btn-primary" href="{C.PLAY}">{e(H['cta'])}</a>
    </div>
    <p class="small">{e(H['small'])}<a href="#keep">{e(H['small_link'])}</a>.</p>
  </div>
  {session_card()}
</section>

<section id="no-account">
  <p class="eyebrow">{e(C.NO_ACCOUNT['eyebrow'])}</p>
  <h2>{e(C.NO_ACCOUNT['h2'])}</h2>
  <div class="stack"><p>{e(C.NO_ACCOUNT['p'])}</p></div>
</section>

<section id="sessions">
  <p class="eyebrow">{e(C.SESSIONS['eyebrow'])}</p>
  <h2>{e(C.SESSIONS['h2'])}</h2>
  <p class="lede">{e(C.SESSIONS['lede'])}</p>
  <div class="tiles">{tiles}</div>
  <div class="stack"><p>{e(C.SESSIONS['extend'])}</p><p>{e(C.SESSIONS['ads'])}</p></div>
</section>

<section id="protects">
  <p class="eyebrow">{e(C.PROTECTS['eyebrow'])}</p>
  <h2>{e(C.PROTECTS['h2'])}</h2>
  <div class="grid three">{protects}</div>
</section>

<section id="keep">
  <p class="eyebrow">{e(C.KEEP['eyebrow'])}</p>
  <h2>{e(C.KEEP['h2'])}</h2>
  <p class="keep">{e(C.TRANSPARENCY)}</p>
  <p class="after">{e(C.KEEP['after'])}<a href="{C.PRIVACY_URL}">{e(C.KEEP['after_link'])}</a>{e(C.KEEP['after_tail'])}</p>
</section>

<section id="wireguard">
  <p class="eyebrow">{e(C.WIREGUARD['eyebrow'])}</p>
  <h2>{e(C.WIREGUARD['h2'])}</h2>
  <div class="stack">
    <p>{e(C.WIREGUARD['p1'])}</p>
    <p>{e(C.WIREGUARD['p2'])}</p>
    <p>Read more at the <a href="{C.WIREGUARD_URL}">{e(C.WIREGUARD['link_text'])}</a>.</p>
  </div>
</section>

<section id="faq">
  <p class="eyebrow">Questions</p>
  <h2>Asked plainly, answered plainly.</h2>
  <div class="faq">{faq}</div>
</section>

<section id="install">
  <p class="eyebrow">{e(C.INSTALL['eyebrow'])}</p>
  <h2>{e(C.INSTALL['h2'])}</h2>
  <div class="install">
    <a class="badge-link" href="{C.PLAY}"><img src="/assets/img/google-play-badge.png" alt="Get it on Google Play" width="194" height="75"></a>
    <p>{e(C.INSTALL['p'])}</p>
  </div>
</section>
"""
    write("index.html", layout(
        path="/", title=C.HOME_TITLE, description=C.HOME_DESC, body=body,
        ld=[ld_app()], og="og-home.png", nav_current="/",
        extra_head="", ) .replace("</body>", COUNTDOWN_JS + "\n</body>"))


def build_download() -> None:
    nav_page("/download/", "Download")
    D = C.DOWNLOAD
    body = f"""
<section class="hero" style="grid-template-columns:1fr;padding-block:48px 40px">
  <div>
    <p class="eyebrow">Download</p>
    <h1>{e(D['h1'])}</h1>
    <p class="lede">{e(D['lede'])}</p>
    <div class="actions">
      <a class="badge-link" href="{C.PLAY}"><img src="/assets/img/google-play-badge.png" alt="Get it on Google Play" width="194" height="75"></a>
    </div>
    <dl class="facts">
      <dt>Current version</dt><dd>{e(VERSION_NAME)} (build {VERSION_CODE}), released {RELEASE_DATE}</dd>
      <dt>Requires</dt><dd>{e(C.MIN_ANDROID)}</dd>
      <dt>Age</dt><dd>You must be {e(C.MIN_AGE)} to use NetCloak</dd>
      <dt>Price</dt><dd>Free, supported by rewarded video ads that you can decline by letting a session end</dd>
      <dt>Server</dt><dd>One, in New York, United States</dd>
    </dl>
  </div>
</section>

<section>
  <p class="eyebrow">APK</p>
  <h2>{e(D['no_apk_h'])}</h2>
  <div class="stack"><p>{e(D['no_apk_p'])}</p></div>
</section>

<section id="keep">
  <p class="eyebrow">{e(C.KEEP['eyebrow'])}</p>
  <h2>{e(C.KEEP['h2'])}</h2>
  <p class="keep">{e(C.TRANSPARENCY)}</p>
  <p class="after">{e(C.KEEP['after'])}<a href="{C.PRIVACY_URL}">{e(C.KEEP['after_link'])}</a>{e(C.KEEP['after_tail'])}</p>
</section>
"""
    write("download/index.html", layout(
        path="/download/", title=C.DOWNLOAD_TITLE, description=C.DOWNLOAD_DESC, body=body,
        ld=[ld_app()], og="og-download.png", nav_current="/download/"))


# ==================================================================================================
# Legal — mirrored from legal.neuera.app, which is the source of truth
# ==================================================================================================

LEGAL = {
    "privacy": {
        "source": C.PRIVACY_URL, "label": "Privacy Policy",
        "title": "Privacy Policy · NetCloak VPN",
        "desc": "What NetCloak keeps and what it does not: no browsing or DNS logs, a session "
                "record deleted when the session ends, operational logs kept two days.",
    },
    "terms": {
        "source": C.TERMS_URL, "label": "Terms of Use",
        "title": "Terms of Use · NetCloak VPN",
        "desc": "The rules for using NetCloak: who may use it, how timed sessions and "
                "extensions work, acceptable use, and when a session can end early.",
    },
}
CACHE = Path(__file__).resolve().parent / "legal_cache"
# The hub marks the privacy article with one class and the terms article with another.
ARTICLE_RE = re.compile(
    r'<article\s+class="(?:legal-document current-document|policy-content)"[\s\S]*?</article>',
    re.I)


def sync_legal() -> None:
    """Re-fetch both documents into the committed cache. The build itself never fetches."""
    import urllib.request

    CACHE.mkdir(parents=True, exist_ok=True)
    for kind, meta in LEGAL.items():
        req = urllib.request.Request(meta["source"], headers={"User-Agent": "netcloak.app build"})
        with urllib.request.urlopen(req, timeout=30) as r:
            if r.status != 200:
                raise SystemExit(f"sync_legal: {meta['source']} returned {r.status}")
            text = r.read().decode("utf-8")
        m = ARTICLE_RE.search(text)
        if not m:
            raise SystemExit(f"sync_legal: no document article at {meta['source']}")
        body = m.group(0)
        body = re.sub(r"<script[\s\S]*?</script>", "", body, flags=re.I)
        body = re.sub(r'\son\w+="[^"]*"', "", body, flags=re.I)
        body = body.replace(C.PRIVACY_URL, "/privacy/").replace(C.TERMS_URL, "/terms/")
        body = body.replace('href="/netcloak/privacy/"', 'href="/privacy/"')
        body = body.replace('href="/netcloak/terms/"', 'href="/terms/"')
        body = body.replace('href="./archive.html"', f'href="{meta["source"]}archive.html"')
        (CACHE / f"{kind}.html").write_text(body, encoding="utf-8")
        print(f"  synced {kind} from {meta['source']} ({len(body):,} bytes)")


def build_legal() -> None:
    for kind, meta in LEGAL.items():
        cached = CACHE / f"{kind}.html"
        if not cached.exists():
            raise SystemExit(f"missing {cached.relative_to(ROOT)} — run: python3 site/build.py --sync-legal")
        body = cached.read_text(encoding="utf-8")
        page = f"""
<section class="legal">
  <p class="eyebrow">Legal</p>
  <p class="notice">This is a copy of the {e(meta['label'])} published at
  <a href="{meta['source']}">legal.neuera.app/netcloak/{kind}/</a>, which is the canonical
  version and keeps every past version readable.</p>
  {body}
</section>
"""
        write(f"{kind}/index.html", layout(
            path=f"/{kind}/", title=meta["title"], description=meta["desc"], body=page,
            og="og-home.png", canonical=meta["source"], in_sitemap=False))


def build_404() -> None:
    body = f"""
<section class="hero" style="grid-template-columns:1fr">
  <div>
    <p class="eyebrow">404</p>
    <h1>{e(C.NOT_FOUND['h1'])}</h1>
    <p class="lede">{e(C.NOT_FOUND['p'])}</p>
    <div class="actions">
      <a class="btn btn-primary" href="/">Home</a>
      <a class="btn btn-ghost" href="/download/">Download</a>
      <a class="btn btn-ghost" href="/privacy/">Privacy Policy</a>
      <a class="btn btn-ghost" href="/terms/">Terms of Use</a>
      <a class="btn btn-ghost" href="{C.LEGAL_HUB}">Legal hub</a>
    </div>
  </div>
</section>
"""
    write("404.html", layout(
        path="/404.html", title=C.NOT_FOUND_TITLE,
        description="That page does not exist on netcloak.app.", body=body,
        og="og-home.png", in_sitemap=False))


# ==================================================================================================
# Sitemap, robots, manifest, IndexNow
# ==================================================================================================

def last_modified(path: str) -> str:
    rel = "index.html" if path == "/" else path.strip("/") + "/index.html"
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", rel], cwd=ROOT,
                             capture_output=True, text=True, timeout=10).stdout.strip()
        if out:
            return out
    except Exception:
        pass
    return datetime.date.today().isoformat()


INDEXNOW_KEY = "6f1c2b8e4d9a4b7c9e3f1a2d5c8b7e64"


def build_indexnow_key() -> None:
    write(f"{INDEXNOW_KEY}.txt", INDEXNOW_KEY + "\n")


def submit_indexnow() -> None:
    """Run with --ping after a deploy. Not part of an ordinary build: it reaches a third party."""
    import urllib.request

    urls = [C.SITE + p["path"] for p in PAGES]
    payload = json.dumps({"host": "netcloak.app", "key": INDEXNOW_KEY,
                          "keyLocation": f"{C.SITE}/{INDEXNOW_KEY}.txt", "urlList": urls}).encode()
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=payload,
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    with urllib.request.urlopen(req, timeout=30) as r:
        print(f"  IndexNow: HTTP {r.status} for {len(urls)} URLs")


def build_sitemap_and_robots() -> None:
    seen, urls = set(), []
    for p in PAGES:
        if p["path"] in seen:
            continue
        seen.add(p["path"])
        urls.append(f"  <url><loc>{C.SITE}{p['path']}</loc><lastmod>{last_modified(p['path'])}</lastmod></url>")
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + "\n".join(urls) + "\n</urlset>\n")
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {C.SITE}/sitemap.xml\n")


def build_manifest() -> None:
    write("site.webmanifest", json.dumps({
        "name": f"{C.NAME} VPN", "short_name": C.NAME,
        "icons": [{"src": "/assets/img/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "/assets/img/icon-512.png", "sizes": "512x512", "type": "image/png"}],
        "theme_color": "#0B1210", "background_color": "#0B1210", "display": "browser",
        "start_url": "/",
    }, indent=1) + "\n")


# ==================================================================================================
# Images — icons from the app's PNG, Open Graph cards drawn with PIL
# ==================================================================================================

SRC_ICON = ROOT / "assets/img/netcloak-icon-512.png"
TTF_CACHE = Path(os.environ.get("PLEX_TTF_DIR", str(ROOT.parent / "plex-ttf")))


def png_bytes(img) -> bytes:
    import io
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def build_icons() -> None:
    try:
        from PIL import Image
    except ImportError:
        print("  icons: PIL not installed, keeping existing files")
        return
    src = Image.open(SRC_ICON).convert("RGBA")
    for name, size in (("favicon-16.png", 16), ("favicon-32.png", 32), ("icon-64.png", 64),
                       ("apple-touch-icon.png", 180), ("icon-192.png", 192), ("icon-512.png", 512)):
        write_bytes(f"assets/img/{name}", png_bytes(src.resize((size, size), Image.LANCZOS)))
    # The old path keeps working for anything that cached it.
    write_bytes("favicon.png", png_bytes(src.resize((64, 64), Image.LANCZOS)))


def font(name: str, size: int):
    from PIL import ImageFont
    p = TTF_CACHE / name
    if p.exists():
        return ImageFont.truetype(str(p), size)
    print(f"  og: {p} missing, falling back to PIL's default font")
    return ImageFont.load_default(size=size)


def og_card(eyebrow: str, headline: str, sub: str) -> bytes:
    from PIL import Image, ImageDraw
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), "#0B1210")
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 14, H], fill="#1EC860")
    icon = Image.open(SRC_ICON).convert("RGBA").resize((96, 96), Image.LANCZOS)
    im.paste(icon, (72, 64), icon)
    d.text((192, 74), "NetCloak", font=font("IBMPlexSans-SemiBold.ttf", 40), fill="#EAF2EC")
    d.text((192, 122), eyebrow.upper(), font=font("IBMPlexMono-Medium.ttf", 22), fill="#5FE08F")
    y = 230
    for line in headline.split("\n"):
        d.text((72, y), line, font=font("IBMPlexSans-SemiBold.ttf", 76), fill="#EAF2EC")
        y += 88
    y += 18
    for line in sub.split("\n"):
        d.text((72, y), line, font=font("IBMPlexSans-Regular.ttf", 30), fill="#B7C4BC")
        y += 42
    d.text((72, 560), "netcloak.app", font=font("IBMPlexMono-Medium.ttf", 24), fill="#8A9890")
    return png_bytes(im)


def build_og() -> None:
    try:
        import PIL  # noqa: F401
    except ImportError:
        print("  og: PIL not installed, keeping existing images")
        return
    write_bytes("assets/img/og-home.png", og_card(
        "Free WireGuard VPN for Android",
        "A VPN that shows\nyou the clock.",
        "No account, no sign-up. Timed sessions you choose.\nOne server, New York. We say what we keep."))
    write_bytes("assets/img/og-download.png", og_card(
        "Download",
        "Get NetCloak on\nGoogle Play.",
        f"Free. Android 8.0 or later. Version {VERSION_NAME}.\nNo APK downloads, by design."))


# ==================================================================================================
# Main
# ==================================================================================================

def check_css(css: str) -> None:
    if css.count("/*") != css.count("*/"):
        raise SystemExit("site.css: unbalanced comment")


def main() -> int:
    global VERSION_NAME, VERSION_CODE, RELEASE_DATE
    if "--sync-legal" in sys.argv:
        sync_legal()
    VERSION_NAME, VERSION_CODE, RELEASE_DATE = app_version()
    check_css(CSS)
    write("assets/site.css", CSS)
    write(".nojekyll", "")
    build_icons()
    build_og()
    build_home()
    build_download()
    build_legal()
    build_404()
    build_manifest()
    build_indexnow_key()
    build_sitemap_and_robots()
    if "--ping" in sys.argv:
        submit_indexnow()

    print(f"{len(PAGES)} indexable page(s)")
    if not _changed:
        print("everything already up to date")
        return 0
    print(f"{'would change' if CHECK else 'wrote'} {len(_changed)} file(s)")
    for f in sorted(_changed):
        print(f"  {f}")
    return 1 if CHECK else 0


if __name__ == "__main__":
    raise SystemExit(main())
