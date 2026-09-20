"""Everything netcloak.app says, in one place.

build.py turns this into HTML. Edit here, never the generated files.

Copy rules, carried from the store listing and the privacy policy rewrite:
active voice; the number before the adjective; the limit stated next to the
benefit. Never "unlimited", never "anonymous", never "no logs" as an absolute,
never "bypass school/work", never a region-switching claim. One server exists,
in New York, and the site says so.
"""

SITE = "https://netcloak.app"
NAME = "NetCloak"
TAGLINE = "A VPN that shows you the clock."
PLAY = "https://play.google.com/store/apps/details?id=app.netcloak"
PACKAGE = "app.netcloak"
LEGAL_HUB = "https://legal.neuera.app/netcloak/"
PRIVACY_URL = "https://legal.neuera.app/netcloak/privacy/"
TERMS_URL = "https://legal.neuera.app/netcloak/terms/"
WIREGUARD_URL = "https://www.wireguard.com/"

ORG = {
    "name": "NeuEra Apps",
    "legalName": "NeuEra Apps LLC",
    "email": "hello@neuera.app",
    "url": "https://neuera.app/",
}

# Public verification token for https://netcloak.app/ from the Site Verification API.
# Not a secret: it only proves to Google that whoever holds the domain put it there.
SEARCH_CONSOLE_META_CONTENT = "QdiSCBEV68PdCPjb2iDeEWH348pYsWWqdlfs9gpHWXM"

# The last values seen from the Play Developer API. The build refreshes the version
# name and code from the API when PLAY_SA_KEY is set; the API carries no release date,
# so the date is kept here and moved forward by hand when a new build ships.
APP_VERSION_NAME = "2026.9.6"
APP_VERSION_CODE = 142
APP_RELEASE_DATE = "2026-09-16"
MIN_ANDROID = "Android 8.0 or later"
MIN_AGE = "18 or older"

# Verbatim on every page that talks about data. The same paragraph the store listing
# and the privacy policy use, so no surface can promise more than another.
TRANSPARENCY = (
    "We do not log the sites you visit, your DNS queries, or anything else inside the "
    "tunnel. We cannot read it. We keep a small record while a session is running, "
    "deleted when the session ends. Operational logs that include your IP address are "
    "kept for no more than two days, then deleted. A VPN is not invisibility: it changes "
    "where your traffic joins the public internet, not what you do once it gets there."
)

# Required by the WireGuard trademark policy and by the Google Play brand guidelines.
WIREGUARD_ATTRIBUTION = (
    "“WireGuard” and the “WireGuard” logo are registered trademarks "
    "of Jason A. Donenfeld."
)
PLAY_ATTRIBUTION = "Google Play and the Google Play logo are trademarks of Google LLC."

MODES = [
    # key, name, minutes, speed multiplier, one-line use
    ("marathon", "Marathon", 80, "1×", "Standard speed for the longest stretch."),
    ("balanced", "Balanced", 40, "2×", "Twice the speed. The default."),
    ("sprint", "Sprint", 20, "4×", "Four times the speed for a quick job."),
]
DEFAULT_MODE = "balanced"
MAX_SESSION_HOURS = 3

# ---------------------------------------------------------------------------------------
# Home
# ---------------------------------------------------------------------------------------

HOME_TITLE = "NetCloak: Free WireGuard VPN for Android, No Account"
HOME_DESC = (
    "Free WireGuard VPN for Android with no account and no sign-up. Pick a timed session, "
    "tap once, see the time left. One server in New York. We say what we keep."
)

HERO = {
    "eyebrow": "Free WireGuard® VPN for Android",
    "h1": TAGLINE,
    "sub": (
        "No account, no sign-up. Pick how long you need and how fast, tap once, and see "
        "exactly how much time is left. Extend with a short ad, up to three hours."
    ),
    "cta": "Get it on Google Play",
    "small": "Android 8.0+ · 18+ · One server, New York · What we keep is ",
    "small_link": "one paragraph long",
}

NO_ACCOUNT = {
    "eyebrow": "No account",
    "h2": "Not even an email address.",
    "p": (
        "There is nothing to register and nothing to remember. When you connect, the app "
        "generates a random key for that session and our server hands it a short-lived, "
        "anonymous token. Both are deleted with the session. Nothing about you is stored "
        "between one session and the next, because nothing about you was collected."
    ),
}

SESSIONS = {
    "eyebrow": "How sessions work",
    "h2": "Timed sessions, not data caps.",
    "lede": (
        "Free time arrives in blocks. Before you connect, pick the mode that fits what "
        "you are doing: longer at standard speed, or shorter and faster."
    ),
    "extend": (
        "The app shows the time remaining the whole way and warns you before a session runs "
        "low. Watching a short rewarded video adds another block of your mode’s length. "
        "Remaining time tops out at three hours in one stretch, and reconnecting starts a "
        "fresh session."
    ),
    "ads": (
        "How often an ad is asked for is a setting we control remotely, and it can be zero. "
        "When it is, sessions extend without one."
    ),
}

PROTECTS = {
    "eyebrow": "What it protects",
    "h2": "The network you are on cannot read your traffic.",
    "items": [
        ("Encrypted end to end with the server",
         "Everything travels inside a WireGuard® tunnel encrypted with ChaCha20-Poly1305. "
         "The wifi, the hotspot, or the carrier between you and New York sees only "
         "encrypted packets."),
        ("Built for the wifi you do not control",
         "Airports, cafes, hotels and other open networks are where this matters most. "
         "Connect first, then browse."),
        ("Your address stays behind ours",
         "While you are connected, the sites you visit see the server’s address, not "
         "yours."),
    ],
}

KEEP = {
    "eyebrow": "What we keep",
    "h2": "One paragraph, the same everywhere.",
    "after": "That paragraph is also the one in our ",
    "after_link": "privacy policy",
    "after_tail": ", which says the rest in plain words.",
}

WIREGUARD = {
    "eyebrow": "Built on WireGuard",
    "h2": "Modern, small, and fast on a phone.",
    "p1": (
        "WireGuard® is a VPN protocol with a small codebase, quick connections and "
        "low battery use. It connects in a fraction of a second and costs your phone less "
        "power while it runs than older protocols do."
    ),
    "p2": (
        "NetCloak carries the whole setup. There is no configuration file to import and "
        "no QR code to scan: the key, the address and the server are arranged for each "
        "session when you tap connect."
    ),
    "link_text": "WireGuard project",
}

# Verbatim questions people ask Google, answered honestly. FAQPage schema belongs to
# the dedicated /faq/ page in Pass 2; the home page only shows these as details.
HOME_FAQ = [
    ("Is there a free VPN without making an account?",
     "Yes. NetCloak has no account at all: no email, no password, no sign-up screen. "
     "Install it from Google Play, choose a mode and tap connect."),
    ("Which VPN does not require login?",
     "NetCloak never asks you to log in, because there is nothing to log in to. A "
     "random key and an anonymous token identify the session, and both are deleted "
     "when it ends."),
    ("Is there a free VPN that uses WireGuard?",
     "NetCloak is one. Every connection is a WireGuard® tunnel, and the app arranges "
     "it for you, so you never touch a configuration file."),
    ("Can I use WireGuard on Android?",
     "Yes. The official WireGuard app needs a configuration from a server you already "
     "have. NetCloak includes the server and the configuration, so it works on its own "
     "on Android 8.0 or later."),
    ("Are there any free no log VPNs?",
     "We do not use the phrase, because it hides more than it says. We cannot read what "
     "goes through the tunnel and we do not log the sites you visit. We do keep a small "
     "session record while you are connected, and operational logs with your IP address "
     "for up to two days. That is the whole list."),
]

INSTALL = {
    "eyebrow": "Install",
    "h2": "Free on Google Play.",
    "p": "Android 8.0 or later. You must be 18 or older to use NetCloak.",
}

# ---------------------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------------------

DOWNLOAD_TITLE = "Download · NetCloak VPN"
DOWNLOAD_DESC = (
    "Get NetCloak, the free WireGuard VPN for Android, on Google Play. No account. "
    "Current version, requirements, and why there is no APK download here."
)
DOWNLOAD = {
    "h1": "Get NetCloak on Google Play",
    "lede": "Free, no account, and updated through the store.",
    "no_apk_h": "Why there is no APK download here",
    "no_apk_p": (
        "NetCloak is signed and delivered through Google Play, which is what lets updates "
        "arrive automatically and lets your phone check that the app it installed is the "
        "one we built. Copies on APK download sites are outside that chain: they can be "
        "stale, and they can be altered. If you find one, it is not from us."
    ),
}

# ---------------------------------------------------------------------------------------
# 404
# ---------------------------------------------------------------------------------------

NOT_FOUND_TITLE = "Page not found · NetCloak VPN"
NOT_FOUND = {
    "h1": "That page is not here.",
    "p": "It may have moved, or the address may have a typo. These are the pages that exist.",
}
