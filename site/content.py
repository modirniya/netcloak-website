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

# ---------------------------------------------------------------------------------------
# Pass 2 — the content pages. Each entry: title, description, eyebrow, h1, lede, og card
# lines, nav slot (None = footer only), and a body as a list of blocks. Block shapes:
#   ("h2", text)              ("p", text)               ("qa", question, answer)
#   ("ul", [items])           ("dl", [(term, def)])     ("keep",)  the transparency paragraph
#   ("link", text, href, tail)   ("install",)           ("note", text)
# Text may contain <a> and <strong>; everything else is escaped by build.py.
# ---------------------------------------------------------------------------------------

NAV_ORDER = ["/how-it-works/", "/wireguard/", "/transparency/", "/faq/"]

PAGES = {}

PAGES["/no-account/"] = {
    "title": "Free VPN with No Account, No Sign-Up · NetCloak VPN",
    "desc": ("NetCloak is a free VPN for Android with no account at all: no email, no password, "
             "no login. What identifies a session instead, and why that is enough."),
    "eyebrow": "No account",
    "h1": "A free VPN with no account. Not even an email.",
    "lede": ("Most “no sign-up” VPNs still make one somewhere: an email, a numbered account, a "
             "device licence. NetCloak has nothing to make. Install it, pick a mode, tap connect."),
    "og": ("No account", "A free VPN with\nno account.", "Not even an email. Nothing to register,\nnothing to remember, nothing to leak."),
    "nav": None,
    "body": [
        ("qa", "Is there a free VPN without making an account?",
         "Yes: NetCloak has no account of any kind, so there is no email, no password, no "
         "sign-up screen, and nothing to recover if you lose your phone."),
        ("p", "When you install NetCloak there is no first screen asking who you are. The app "
              "asks Android for permission to run a VPN, shows you the three session modes, and "
              "waits for a tap. That is the whole onboarding."),
        ("h2", "What “no account” means here, and what it means elsewhere"),
        ("p", "The phrase is used loosely across the category, so it is worth being exact. "
              "Windscribe lets you skip the email but still creates an account with a username "
              "and password. Mullvad replaces the email with a random account number that you "
              "have to keep. hide.me advertises no registration on the web, and users report the "
              "Android app asking for an email anyway. None of that is dishonest; it is just a "
              "different thing from having no account."),
        ("p", "NetCloak has no username, no password, no account number and no email field. "
              "There is no server-side profile that could be looked up, exported, breached or "
              "subpoenaed, because one is never created."),
        ("h2", "What identifies a session instead"),
        ("p", "Two things, both temporary. When you tap connect, the app generates a fresh "
              "WireGuard® key pair for that session and sends the public half to our server. "
              "The server hands back a short-lived access token whose subject is an anonymous "
              "identifier. Those two values let the server route your packets for the length of "
              "the session, and both are deleted with it."),
        ("p", "On the phone itself, the token is held in Android’s hardware-backed encrypted "
              "storage, next to preferences such as your chosen mode and theme. Uninstalling "
              "removes all of it. There is nothing on our side to delete, because nothing about "
              "you was kept."),
        ("h2", "Why this is possible"),
        ("p", "Accounts exist to tie a person to a payment, to sync settings between devices, or "
              "to sell to. NetCloak does none of those. Nothing is sold, nothing is synced, and "
              "the ads that pay for the server are shown by Google AdMob against an advertising "
              "identifier you can reset in Android settings, not against a profile of you."),
        ("qa", "Which VPN does not require login?",
         "NetCloak never shows a login screen, because there is nothing to log in to: a random "
         "key and a short-lived anonymous token identify each session, and both are deleted "
         "when it ends."),
        ("link", "Everything the server does keep, for how long, is listed on the ",
         "/transparency/", "transparency page", "."),
        ("install",),
    ],
}

PAGES["/how-it-works/"] = {
    "title": "How Sessions Work · NetCloak VPN",
    "desc": ("NetCloak sessions are timed, not data-capped: 80, 40 or 20 minutes at rising "
             "speed, extended by a short ad up to three hours. When a session ends early, and why."),
    "eyebrow": "How it works",
    "h1": "Timed sessions, three speeds, one tap.",
    "lede": ("Free time arrives in blocks. You choose the block before you connect, the app shows "
             "the countdown the whole way, and a short ad buys another block when you need it."),
    "og": ("How it works", "Timed sessions,\nthree speeds.", "80, 40 or 20 minutes at rising speed.\nExtend with a short ad, up to three hours."),
    "nav": 0,
    "body": [
        ("h2", "Pick a mode"),
        ("p", "Each mode trades time for speed. Marathon gives 80 minutes at the base speed. "
              "Balanced, the default, gives 40 minutes at twice that. Sprint gives 20 minutes at "
              "four times the base speed, for a download you want done now. The choice is made "
              "before you connect and stays fixed for the session; to change it, end the session "
              "and start another."),
        ("modes",),
        ("h2", "Time remaining, and the warnings"),
        ("p", "The app shows the time left in the status line, in the progress bar, and in the "
              "ongoing notification, all driven by the same one-second countdown against the "
              "expiry the server set. Our server marks a session “low” when 15% of its window "
              "remains and “critical” at 5%. Those levels change the colour of the bar and show "
              "a prompt to extend. They never end the session; the clock does that."),
        ("h2", "Extending with an ad"),
        ("p", "When time is running low, watching a short rewarded video adds another block of "
              "your mode’s length: 80, 40 or 20 minutes. Remaining time is capped at three hours "
              "in one stretch, so an extension can add less than a full block, or nothing at all. "
              "When that happens the app tells you exactly how much was added instead of "
              "pretending."),
        ("p", "How often an ad is required is a setting we control remotely, and it can be "
              "zero. When it is zero, extensions are granted without one. When it is one, every "
              "extension asks for one. We publish the current state on the transparency page "
              "whenever it changes."),
        ("h2", "Why a session can end early"),
        ("p", "The server, not the app, owns expiry, and it ends a session before its time in "
              "six situations. Each one frees the server for someone else:"),
        ("ul", [
            "<strong>Time ran out.</strong> The ordinary end. The app disconnects about thirty "
            "seconds before the server does, so you are never cut off mid-transfer.",
            "<strong>The tunnel went idle.</strong> No WireGuard® handshake for five minutes, "
            "which usually means the phone lost its network or went to sleep.",
            "<strong>It never connected.</strong> A session was created but no handshake arrived "
            "within three minutes.",
            "<strong>A newer session replaced it.</strong> One session per user is active at a "
            "time; starting another ends the previous one.",
            "<strong>The server is under capacity pressure.</strong> Idle sessions are reclaimed "
            "first when the server is full.",
            "<strong>A peer was left behind.</strong> A failure on our side left a tunnel with no "
            "live session attached; it is cleaned up.",
        ]),
        ("p", "Reconnecting after any of these starts a fresh session with a fresh key."),
        ("h2", "When the tunnel dies"),
        ("p", "If your phone loses its network for longer than the idle limit, the server "
              "reclaims the session. When the network returns, the tunnel on the phone is still "
              "up but carries nothing. NetCloak watches for exactly this: it reads how long ago "
              "the tunnel last completed a handshake, checks that the phone has a working network "
              "outside the VPN, and confirms that its own status checks are failing. When all "
              "three hold, it ends the session and shows a notice saying the connection was lost, "
              "rather than leaving a screen that says “Protected” over a dead tunnel. It does not "
              "reconnect by itself, because that would spend a new session, and possibly an ad, "
              "without asking you."),
        ("link", "What the server keeps while a session runs is on the ",
         "/transparency/", "transparency page", ". The exact rules are in the "
         "<a href=\"/terms/\">terms of use</a>."),
        ("install",),
    ],
}

PAGES["/wireguard/"] = {
    "title": "WireGuard VPN for Android, No Config File · NetCloak VPN",
    "desc": ("NetCloak is a free WireGuard VPN for Android that needs no configuration file and "
             "no QR code. What WireGuard is, why it suits a phone, and where it has limits."),
    "eyebrow": "WireGuard",
    "h1": "WireGuard® on Android, without the configuration file.",
    "lede": ("Search for WireGuard on Android and you find setup guides, tunnel files and QR "
             "codes. NetCloak ships the protocol with all of that already done."),
    "og": ("WireGuard on Android", "WireGuard, without\nthe config file.", "The protocol the fast VPNs use,\narranged for you on every connect."),
    "nav": 1,
    "body": [
        ("qa", "Is there a free VPN that uses WireGuard?",
         "Yes: every NetCloak connection is a WireGuard tunnel, built with the official Android "
         "tunnel library from wireguard.com, and the app arranges the key, the address and the "
         "server for you on every connect."),
        ("h2", "What WireGuard is"),
        ("p", "WireGuard is a VPN protocol and the reference software that implements it, "
              "published at <a href=\"https://www.wireguard.com/\">wireguard.com</a>. It is "
              "deliberately small: a few thousand lines where older protocols run to hundreds of "
              "thousands, which makes it easier to audit and harder to misconfigure. It is part "
              "of the Linux kernel, and its Android implementation is the library NetCloak ships."),
        ("h2", "Why it suits a phone"),
        ("p", "A phone changes networks constantly, from wifi to mobile data and back, and "
              "sleeps between uses. WireGuard handles both well. A connection completes in a "
              "single round trip, so reconnecting after a network change takes a fraction of a "
              "second. The tunnel is keyed to the device rather than to a network address, so "
              "moving between wifi and cellular does not drop it. And because the protocol does "
              "little work per packet, it costs the battery less than the alternatives while it "
              "runs."),
        ("h2", "No config file, no QR code"),
        ("p", "The official WireGuard app expects you to bring your own server and import a "
              "configuration file or scan a QR code that describes it. That is the right design "
              "for people who run their own servers, and the wrong one for everyone else. "
              "NetCloak includes the server, generates a fresh key pair on the phone for each "
              "session, and exchanges the public halves with the server when you tap connect. "
              "You never see a configuration, because there is nothing for you to get wrong."),
        ("h2", "The encryption, in one paragraph"),
        ("p", "WireGuard encrypts every packet with ChaCha20 and authenticates it with Poly1305, "
              "a combination chosen for speed on processors without dedicated encryption "
              "hardware, which describes most phones. Keys are exchanged with Curve25519 and "
              "rotated regularly, so a key captured today cannot decrypt yesterday’s traffic. "
              "The network you are on, the hotspot, the cafe, the carrier, sees only encrypted "
              "packets addressed to our server in New York."),
        ("h2", "Where it has limits"),
        ("p", "WireGuard’s own <a href=\"https://www.wireguard.com/known-limitations/\">known "
              "limitations page</a> is honest and short, and so is this. The protocol is not "
              "post-quantum secure by default; NetCloak does not add a pre-shared key on top, so "
              "neither is NetCloak. WireGuard traffic has a recognisable shape on the wire, which "
              "means a network that wants to know you are using a VPN can tell; it cannot read "
              "what is inside. And a VPN protects the path between your phone and our server, not "
              "what you do once your traffic leaves it."),
        ("h2", "WireGuard versus OpenVPN"),
        ("p", "OpenVPN is older, larger, and more configurable; it can run over TCP, wear more "
              "cipher suites, and hide inside ordinary HTTPS traffic in ways WireGuard cannot. "
              "WireGuard is faster, connects quicker, uses less battery, and has far less code to "
              "audit. For a phone that roams between networks, those are the properties that "
              "matter, which is why NetCloak uses WireGuard and nothing else."),
        ("qa", "Can I use WireGuard on Android?",
         "Yes: Android 8.0 and later support it through the VPN service API, and NetCloak "
         "includes the server side too, so it works on its own without a configuration."),
        ("qa", "Is WireGuard free or paid?",
         "The protocol and its software are free and open source; NetCloak, which is built on "
         "them, is free as well, paid for by rewarded ads rather than by you."),
        ("install",),
    ],
}

PAGES["/transparency/"] = {
    "title": "Transparency: What NetCloak Keeps · NetCloak VPN",
    "desc": ("Every field the NetCloak server stores while a session runs, how long logs are "
             "kept, where the server is, who else touches data, and what we cannot see."),
    "eyebrow": "Transparency",
    "h1": "What we keep, for how long, and who else sees it.",
    "lede": ("This page is the privacy policy with the lawyers’ sentences taken out. Nothing here "
             "says less than the policy, and nothing here says more."),
    "og": ("Transparency", "What we keep,\nand for how long.", "Every field, every log, every third party,\nand what we cannot see."),
    "nav": 2,
    "body": [
        ("keep",),
        ("qa", "Are there any free no log VPNs?",
         "We do not use the phrase, because every VPN keeps something while you are connected; "
         "instead, here is the complete list of what NetCloak keeps, which is short, and how "
         "long each item lives."),
        ("h2", "The session record, field by field"),
        ("p", "While a session is running, our server holds one row for it. These are its "
              "fields, in full:"),
        ("dl", [
            ("WireGuard® public key", "Generated on your phone for this session. Identifies the "
             "tunnel, not you."),
            ("Tunnel address", "A private address in the 10.8.x.x range assigned inside the "
             "tunnel. It is not your public address."),
            ("Created, expires, last active", "Three timestamps. They are how the server knows "
             "when to end the session and whether the tunnel has gone idle."),
            ("Extension count", "How many times the session was extended."),
            ("Anonymous identifier", "The subject of your access token: a random value with no "
             "link to a person, account, or email."),
            ("Bytes transferred", "Measured against a fair-use ceiling of 10 GB per session, "
             "which exists so that one session cannot exhaust a shared server. It is not a "
             "quota and the app does not show it."),
            ("Mode", "Marathon, Balanced or Sprint."),
        ]),
        ("p", "The row is deleted when the session ends, for any of the reasons on the "
              "<a href=\"/how-it-works/\">how it works</a> page."),
        ("h2", "Logs, and the two-day rule"),
        ("p", "Our server writes operational logs: which requests arrived, which were refused by "
              "the rate limiter, which sessions were created and reclaimed. Those logs contain "
              "your public IP address, because that is what a request arrives from. They are "
              "kept for no more than two days and then deleted. Rate limits are five requests a "
              "minute per address for creating or extending a session and thirty for checking "
              "its status."),
        ("p", "There are no browsing logs, no DNS query logs, and no record of traffic content. "
              "This is not a policy choice we could quietly reverse; the traffic is encrypted "
              "with a key we do not hold, so there is nothing to record."),
        ("h2", "The server"),
        ("p", "One, in New York, United States, rented from Contabo GmbH, a hosting company "
              "based in Germany. We say this plainly because “servers in 90 countries” is the "
              "kind of sentence that usually hides rented capacity and virtual locations. Ours "
              "is one machine, we know exactly where it is, and everyone connects to it."),
        ("h2", "Who else touches data, and what each receives"),
        ("dl", [
            ("Google AdMob and User Messaging Platform", "Serve the rewarded video ads and "
             "collect your consent choice. AdMob receives your device’s advertising identifier, "
             "which you can reset or delete in Android settings. When an ad reward is verified, "
             "the app attaches a random single-use number and the anonymous identifier from your "
             "token, and Google calls our server to confirm the reward. Nothing about your "
             "browsing reaches AdMob, because it does not pass through the app."),
            ("Cloudflare", "Runs the DNS-over-HTTPS resolver at 1.1.1.1 the app uses to find "
             "its server list and settings. Like any DNS query, that tells Cloudflare which "
             "record was asked for, from which network address."),
            ("Google Play", "Distributes the app under its own terms and sees the install."),
            ("Contabo GmbH", "Hosts the server. Sees the machine, not the contents of the "
             "tunnel."),
        ]),
        ("p", "There is no analytics provider, no crash-reporting service, and no payment "
              "processor, because the app sends no analytics, reports no crashes to a third "
              "party, and sells nothing."),
        ("h2", "What we cannot see"),
        ("p", "The sites you visit, the apps you use, the content of anything you send or "
              "receive, your DNS queries, and your location beyond the coarse fact of which "
              "network address you connected from. The tunnel is encrypted end to end between "
              "your phone and our server with a key your phone generated. We can see that a "
              "tunnel exists and how many bytes have crossed it. That is all."),
        ("h2", "Legal requests"),
        ("p", "Legal requests received to date: 0 (as of 2026-09-20). This line is updated "
              "whenever that changes. What could be produced in response is limited by what "
              "exists: a session row that lives for the length of a session, and operational "
              "logs that live for two days."),
        ("h2", "How the app uses Android’s VPN service"),
        ("p", "NetCloak uses Android’s VpnService to route the device’s traffic through an "
              "encrypted tunnel to our server. It does not redirect, inspect or manipulate the "
              "traffic of other apps for advertising or any other purpose, and it does not "
              "inject anything into it. This is the same statement we make to Google Play in the "
              "VPN declaration every VPN app must file."),
        ("link", "The full privacy policy, with every past version, is at ",
         PRIVACY_URL, "legal.neuera.app", ", and a copy is kept at "
         "<a href=\"/privacy/\">/privacy/</a>."),
    ],
}

FAQ_ITEMS = [
    # Verbatim questions people ask Google, answered first: they are the proposition.
    ("Is there a free VPN without making an account?",
     "Yes. NetCloak has no account at all: no email, no password, no sign-up screen. Install "
     "it from Google Play, choose a mode and tap connect. The only things that identify a "
     "session are a random key and a short-lived anonymous token, both deleted when it ends."),
    ("Which VPN does not require login?",
     "NetCloak never asks you to log in, because there is nothing to log in to. Other free "
     "VPNs that advertise no sign-up usually still create an account behind the scenes, with "
     "an email, a username, or an account number. NetCloak creates none."),
    ("Is there a free VPN that uses WireGuard?",
     "NetCloak is one. Every connection is a WireGuard® tunnel built with the official Android "
     "tunnel library, and the app arranges the key, the address and the server for you, so you "
     "never touch a configuration file or a QR code."),
    ("Can I use WireGuard on Android?",
     "Yes, on Android 8.0 or later. The official WireGuard app needs a configuration from a "
     "server you already have. NetCloak includes the server and the configuration, so it works "
     "on its own."),
    ("Is WireGuard free or paid?",
     "The WireGuard protocol and its software are free and open source. NetCloak, which is "
     "built on them, is free as well and is paid for by rewarded video ads, not by you."),
    ("Are there any free no log VPNs?",
     "We do not use the phrase, because every VPN keeps something while you are connected. "
     "What NetCloak keeps is short: a session record deleted when the session ends, and "
     "operational logs with your IP address for up to two days. We cannot read what goes "
     "through the tunnel and we do not log the sites you visit. The full list is on the "
     "transparency page."),
    # The objections, answered honestly.
    ("Is there a 100% free VPN?",
     "NetCloak costs nothing to install or use. It is paid for by rewarded video ads, which "
     "you watch to extend a session, and the limit is time: 80, 40 or 20 minutes per block "
     "depending on the mode, up to three hours in one stretch. There is no paid tier."),
    ("Can I trust a free VPN?",
     "Trust what a VPN keeps, not what it promises. Read the list of what NetCloak stores, "
     "how long each item lives, and who else touches data, on the transparency page. If a "
     "free VPN will not give you that list, that is your answer."),
    ("What are the risks of using a free VPN?",
     "The usual ones are hidden logging, traffic sold to advertisers, and apps that inject "
     "ads or trackers into your browsing. NetCloak keeps no browsing logs, cannot read the "
     "tunnel, and shows ads only inside the app through Google AdMob, never inside your "
     "traffic. The remaining risk is the one every VPN has: you are trusting the operator "
     "instead of your network. We try to earn that by saying exactly what we keep."),
    ("What are the downsides of using WireGuard VPN?",
     "WireGuard is not post-quantum secure by default, its traffic has a recognisable shape "
     "so a network can tell a VPN is in use, and it runs only over UDP, which some networks "
     "block. Against that, it is faster, connects in a fraction of a second, uses less "
     "battery, and has far less code to audit than older protocols."),
    ("Do Androids have a built-in VPN?",
     "Android has a built-in VPN client for a few enterprise protocols, and a VPN service "
     "API that apps use. It does not include a VPN server, so there is nothing to connect to "
     "without an app and a provider. NetCloak supplies both."),
    ("Is using a VPN illegal in the US?",
     "No. Using a VPN is legal in the United States, Canada, the European Union and most "
     "countries. A few countries restrict or ban them; NetCloak is not distributed in those. "
     "What you do through a VPN is subject to the same laws as what you do without one."),
    # Ours.
    ("Why is there only one server?",
     "Because one is what the service needs today, and saying so is better than inventing "
     "“locations”. It is in New York, and users in the Americas and Europe reach it with "
     "reasonable latency. A second server will come when usage calls for it, and this page "
     "will say where."),
    ("What happens when my time runs out?",
     "The app warns you when 15% of the session remains and again at 5%, and offers an "
     "extension. If you let the clock run out, the app disconnects about thirty seconds before "
     "the server ends the session, so you are not cut off mid-transfer. Reconnecting starts a "
     "fresh session."),
    ("Why does the app need the VPN permission?",
     "Android will not let any app route the device’s traffic without your explicit "
     "permission, which is the dialog you see on first connect. NetCloak uses it to send "
     "traffic through the encrypted tunnel and for nothing else. The permission can be "
     "revoked at any time in Android’s VPN settings."),
    ("Why is it 18+?",
     "Because we want to be able to say plainly who the service is for. NetCloak is an "
     "ad-supported product with a rewarded-video model, and we chose not to design it for "
     "children. The terms of use state the requirement, and the app confirms it on first "
     "launch."),
]

PAGES["/faq/"] = {
    "title": "Questions and Answers · NetCloak VPN",
    "desc": ("Plain answers to the questions people ask about free VPNs, WireGuard on Android, "
             "accounts, logging and limits, as they apply to NetCloak."),
    "eyebrow": "FAQ",
    "h1": "Asked plainly, answered plainly.",
    "lede": ("These are the questions people actually type into a search box, in their own "
             "words, followed by four of ours. Every answer is the same one the privacy policy "
             "would give."),
    "og": ("FAQ", "Asked plainly,\nanswered plainly.", "Sixteen questions about free VPNs, WireGuard,\naccounts and what we keep."),
    "nav": 3,
    "body": [("faq",), ("install",)],
}

PAGES["/about/"] = {
    "title": "About NeuEra Apps · NetCloak VPN",
    "desc": ("NetCloak is made by NeuEra Apps LLC, a small studio that also makes Kalum, "
             "Odometer, Play Lounge and RPS Mafia. Who we are and why a free VPN."),
    "eyebrow": "About",
    "h1": "Made by NeuEra Apps.",
    "lede": ("NetCloak is one of a handful of apps from a small studio that would rather say "
             "exactly what a product does than say it loudly."),
    "og": ("About", "Made by\nNeuEra Apps.", "A small studio. Five apps.\nPlain statements of what each one keeps."),
    "nav": None,
    "body": [
        ("h2", "Who we are"),
        ("p", "NetCloak is published by NeuEra Apps LLC. You can reach us at "
              "<a href=\"mailto:hello@neuera.app\">hello@neuera.app</a>; that address is read "
              "by the people who build the app, not by a ticketing system. The terms of use are "
              "governed by California law. Our legal documents for every app, with every past "
              "version kept readable, live at <a href=\"https://legal.neuera.app/\">"
              "legal.neuera.app</a>."),
        ("h2", "Why a free VPN"),
        ("p", "Because the free ones we tried either asked for an account, hid their limits, or "
              "promised things no VPN can deliver. We wanted one that a person could install "
              "without giving anything up, that showed its limit as a clock rather than hiding a "
              "cap, and that could put its entire data practice in one paragraph. That paragraph "
              "is on every page of this site."),
        ("h2", "The other apps"),
        ("dl", [
            ("Kalum", "International calling. <a href=\"https://kalum.app/\">kalum.app</a>"),
            ("Odometer", "Mileage and expense tracking. "
             "<a href=\"https://odometer.pro/\">odometer.pro</a>"),
            ("Play Lounge", "A board game bundle. "
             "<a href=\"https://playlounge.live/\">playlounge.live</a>"),
            ("RPS Mafia", "A social deduction game with live voice. "
             "<a href=\"https://rpsociety.app/\">rpsociety.app</a>"),
        ]),
        ("p", "All of them follow the same data charter, published on the legal hub, which "
              "sets a test for what may be collected before the first row is written."),
        ("link", "Questions about NetCloak specifically go to the ",
         "/support/", "support page", "."),
    ],
}

PAGES["/support/"] = {
    "title": "Support · NetCloak VPN",
    "desc": ("Known limits of NetCloak, how to report a problem so it can be fixed, and how to "
             "reach the people who make it."),
    "eyebrow": "Support",
    "h1": "Something not working?",
    "lede": ("Most questions are answered on the FAQ or transparency pages. For everything else, "
             "here is what to check and how to reach us."),
    "og": ("Support", "Something\nnot working?", "Known limits, what to include in a report,\nand how to reach a person."),
    "nav": None,
    "body": [
        ("h2", "Known limits"),
        ("ul", [
            "<strong>One server, in New York.</strong> Latency from far away is real, and "
            "there is no region to switch to.",
            "<strong>Android only.</strong> There is no iOS, desktop, router or TV version.",
            "<strong>Timed sessions.</strong> 80, 40 or 20 minutes per block depending on the "
            "mode, up to three hours in one stretch. Extending may require a short ad.",
            "<strong>18 or older.</strong> The terms require it and the app confirms it.",
            "<strong>UDP only.</strong> WireGuard® runs over UDP; a network that blocks it "
            "blocks NetCloak too.",
        ]),
        ("h2", "Reporting a problem"),
        ("p", "Email <a href=\"mailto:hello@neuera.app\">hello@neuera.app</a> with as much of "
              "the following as you can. Each item shortens the time to a fix:"),
        ("ul", [
            "Your Android version, and the phone model.",
            "The NetCloak version, from the download page or the Play Store listing.",
            "The mode you were in: Marathon, Balanced or Sprint.",
            "What the screen said, word for word, and what you expected instead.",
            "Roughly when it happened, in your local time, so we can find the two days of "
            "operational logs that might still exist.",
        ]),
        ("p", "Please do not send screenshots of anything you would not want in an email. We "
              "never need your browsing history, and we cannot see it anyway."),
        ("h2", "Before you write"),
        ("ul", [
            "If the app says the connection was lost, that is the app working as designed after "
            "a long network outage. Tap connect again.",
            "If a session ended sooner than you expected, the "
            "<a href=\"/how-it-works/\">how it works</a> page lists every reason that can "
            "happen.",
            "If you want to know what the server stores, the "
            "<a href=\"/transparency/\">transparency page</a> lists every field.",
            "The <a href=\"/faq/\">FAQ</a> answers the sixteen questions we hear most.",
        ]),
    ],
}


# ==================================================================================================
# Blog — three launch articles. Each answers a question the search results pose and links to the
# product page it supports. Blocks are the same kinds PAGES uses; "p" text is raw HTML so a source
# can be linked inline where a fact is not ours.
# ==================================================================================================

WG_KNOWN_LIMITS = "https://www.wireguard.com/known-limitations/"
WG_PROTOCOL = "https://www.wireguard.com/protocol/"
WG_PAPER = "https://www.wireguard.com/papers/wireguard.pdf"
WG_FORMAL = "https://www.wireguard.com/formal-verification/"
WG_PERF = "https://www.wireguard.com/performance/"
NOISE_URL = "https://noiseprotocol.org/"
PLAY_VPN_POLICY = "https://support.google.com/googleplay/android-developer/answer/12564964"
PLAY_AD_ID_HELP = "https://support.google.com/googleplay/answer/3405269"
PROTON_FREE_MONEY = "https://protonvpn.com/blog/how-do-free-vpns-make-money"
NORTON_FREE_SAFE = "https://us.norton.com/blog/vpn/are-free-vpns-safe"

BLOG_TITLE = "Blog · NetCloak VPN"
BLOG_DESC = ("Plain answers about WireGuard, what makes a VPN protocol safe, and how a free VPN "
             "pays for itself. Written by the people who run NetCloak, dated, and kept current.")

ARTICLES = {}

ARTICLES["/blog/what-is-wireguard/"] = {
    "title": "What is WireGuard, and what does it mean for your phone? · NetCloak VPN",
    "desc": ("WireGuard is a VPN protocol and the software that implements it. What that means on "
             "an Android phone: battery, roaming between wifi and mobile, and the one thing an app "
             "has to watch for."),
    "eyebrow": "WireGuard, explained",
    "h1": "What is WireGuard, and what does it mean for your phone?",
    "lede": ("Most explanations of WireGuard® were written for people running servers. This one is "
             "for the person holding a phone."),
    "published": "2026-09-19",
    "og": ("WireGuard, explained", "What is WireGuard,\nand what does it\nmean for your phone?",
           "The protocol, the cryptography by name, and the\nmobile consequences nobody writes about."),
    "body": [
        ("p", f'WireGuard® is a VPN protocol and the software that implements it, created by Jason A. '
              f'Donenfeld and included in the Linux kernel since version 5.6. A protocol is the set of '
              f'rules two computers follow to build an encrypted tunnel between them; the software is '
              f'the code that follows those rules. WireGuard is unusual in that the '
              f'<a href="{WG_PAPER}">rules fit in a short paper</a> and the reference code is small '
              f'enough to read in an afternoon, which is the property everything else here follows from.'),
        ("h2", "A protocol is not an app"),
        ("p", "When an app such as NetCloak says it uses WireGuard, it means the tunnel between your "
              "phone and the server speaks WireGuard. The app around that tunnel, with its buttons, "
              "its session clock and its ads, is the app maker's own work. Two apps can both use "
              "WireGuard and behave nothing alike, and the protocol says nothing about what the "
              "operator keeps on the server at the far end. Those are separate questions, and this "
              "article is only about the first one."),
        ("h2", "Why the size of the code matters"),
        ("p", f'The Linux implementation of WireGuard is a few thousand lines of code. The protocols '
              f'it replaced run to hundreds of thousands. That is not a boast about elegance; it is a '
              f'statement about who can check it. A security researcher can read the whole of '
              f'WireGuard and hold it in their head, which is why it was reviewed thoroughly enough to '
              f'be accepted into the kernel that runs most of the internet. The project lists the '
              f'<a href="{WG_FORMAL}">formal verification work</a> done on the protocol itself.'),
        ("h2", "The cryptography, by name"),
        ("p", f'WireGuard does not negotiate ciphers. It uses one fixed set, chosen for being fast on '
              f'ordinary processors without special hardware, which is exactly the processor in a '
              f'phone. The <a href="{WG_PROTOCOL}">protocol page</a> lists them; here is what each does.'),
        ("ul", [
            f'<strong>Noise framework.</strong> The <a href="{NOISE_URL}">Noise</a> handshake pattern '
            f'that lets two parties who know each other\'s public keys agree on a shared secret in one '
            f'round trip.',
            '<strong>Curve25519.</strong> The elliptic curve used for that key agreement. Your phone '
            'and the server each generate a private key, exchange public keys, and arrive at the '
            'same secret without ever sending it.',
            '<strong>ChaCha20-Poly1305.</strong> ChaCha20 scrambles every packet with that secret; '
            'Poly1305 stamps each packet with a check so a tampered packet is thrown away rather '
            'than decrypted. On a phone this runs faster than AES without a hardware helper.',
            '<strong>BLAKE2s.</strong> The hash function used inside the handshake to mix keys and '
            'derive new ones.',
        ]),
        ("h2", "What a handshake every two minutes means for your battery"),
        ("p", "WireGuard rotates its session keys by performing a fresh handshake roughly every two "
              "minutes while traffic flows, and only when traffic flows. If your phone is idle, so is "
              "the tunnel: no keepalive chatter, no timers waking the radio. That is why a WireGuard "
              "tunnel left connected overnight costs noticeably less battery than the older designs "
              "that held a session open with constant heartbeats. The project's own "
              f'<a href="{WG_PERF}">performance page</a> covers throughput; the battery effect on a '
              'phone comes from the silence.'),
        ("h2", "Roaming: wifi to mobile without dropping"),
        ("p", "Older VPN protocols bind a tunnel to your IP address, so when your phone leaves the "
              "wifi and picks up mobile data the tunnel breaks and has to be rebuilt. WireGuard "
              "identifies you by your public key, not your address. When the phone moves networks, the "
              "next encrypted packet simply arrives from a new address and the server updates its "
              "notion of where you are. From the phone's side, the tunnel never went away."),
        ("h2", "The silent tunnel: the one thing an app has to watch"),
        ("p", "That same design has a consequence that most VPN apps handle badly. WireGuard has no "
              "concept of a connection being \"up\" or \"down\"; there is only the last time a "
              "handshake succeeded. If the server removes your key, or the network quietly stops "
              "delivering packets, the tunnel on your phone stays configured and keeps reporting "
              "itself as connected while carrying nothing. The protocol will never tell the app. The "
              "app has to watch the handshake age itself and decide when silence has gone on too "
              "long. NetCloak does exactly that: when a tunnel has not handshaked for three minutes on "
              "a network that is otherwise working, it ends the session and tells you, rather than "
              "showing a green shield over a dead connection."),
        ("qa", "What's the difference between VPN and WireGuard?",
         "A VPN is the thing you want: an encrypted tunnel that carries your traffic to another "
         "computer before it reaches the internet. WireGuard is one way of building that tunnel, "
         "alongside OpenVPN and IKEv2. Every WireGuard app is a VPN; not every VPN uses WireGuard."),
        ("h2", "What WireGuard does not do"),
        ("p", f'It is worth being as exact about the limits as about the strengths, and the project '
              f'is, on its <a href="{WG_KNOWN_LIMITS}">Known Limitations page</a>.'),
        ("ul", [
            "<strong>It does not make you anonymous.</strong> The server at the far end sees your "
            "real address, because it has to send packets back to you. What that server keeps is "
            "the operator's decision, not the protocol's.",
            "<strong>It does not hide that you are using a VPN.</strong> WireGuard packets have a "
            "recognisable shape on the wire. Anyone watching your connection can tell a tunnel is "
            "there, even though they cannot see inside it.",
            "<strong>It is not post-quantum by default.</strong> Curve25519 would not survive a "
            "large quantum computer. The protocol has an optional pre-shared key to add a "
            "quantum-resistant layer, which most consumer apps, NetCloak included, do not use today.",
        ]),
        ("h2", "How NetCloak uses it"),
        ("p", "NetCloak ships the official WireGuard tunnel library for Android and nothing else: no "
              "config files to import, no QR codes, no second protocol to fall back to. When you tap "
              "connect, the app generates a fresh key for that session, the server hands back the "
              "tunnel settings, and the tunnel is up. When the session ends the key is thrown away. "
              "The rest of what the app does around the tunnel, the timed sessions and the clock, is "
              "described on the <a href=\"/wireguard/\">WireGuard page</a> and "
              "<a href=\"/how-it-works/\">how it works</a>."),
    ],
}

ARTICLES["/blog/is-wireguard-safe/"] = {
    "title": "Is WireGuard safe? · NetCloak VPN",
    "desc": ("Yes, for what it is designed to do. What safe means for a VPN protocol, what has been "
             "proved about WireGuard, and the specific limits the project itself publishes."),
    "eyebrow": "WireGuard, examined",
    "h1": "Is WireGuard safe?",
    "lede": ("A one-word answer would be dishonest in both directions. Here is what has been proved, "
             "what has not, and where the real risk sits."),
    "published": "2026-09-19",
    "og": ("WireGuard, examined", "Is WireGuard\nsafe?",
           "What has been proved, what has not,\nand where the real risk actually sits."),
    "body": [
        ("p", "Yes: WireGuard® is safe for what it is designed to do, which is to carry your traffic "
              "to a server you have chosen so that nobody in between can read or alter it. The limits "
              "below are real, published by the project itself, and none of them is a hole in that "
              "promise. The risk that matters most is not in the protocol at all."),
        ("h2", "What \"safe\" means for a VPN protocol"),
        ("p", "Three things. Confidentiality: nobody between your phone and the server can read the "
              "traffic. Integrity: nobody can change it in transit without the change being detected "
              "and the packet discarded. Authentication: your phone is talking to the server it "
              "thinks it is, and the server knows which key it is talking to. A protocol that delivers "
              "all three is doing its job. Whether the server at the far end is trustworthy is a "
              "different question, covered at the end."),
        ("h2", "What has been proved"),
        ("p", f'WireGuard\'s handshake is built on the <a href="{NOISE_URL}">Noise protocol '
              f'framework</a>, and the project publishes '
              f'<a href="{WG_FORMAL}">formal verification</a> of the protocol: machine-checked proofs '
              f'that the handshake provides the properties above, including forward secrecy, so that '
              f'a key stolen tomorrow does not decrypt traffic captured today. Very few VPN protocols '
              f'have that. The <a href="{WG_PAPER}">original paper</a> describes the design and the '
              f'reasoning behind each choice.'),
        ("h2", "Forward secrecy, in one paragraph"),
        ("p", "The property people most often mean by \"safe\" without naming it is this: if "
              "someone records your encrypted traffic today and steals a key tomorrow, can they go "
              "back and read what they recorded? With WireGuard, no. Each session's traffic keys are "
              "derived during the handshake from fresh, short-lived values, and the handshake repeats "
              "about every two minutes, so a compromised long-term key unlocks nothing that was "
              "captured before. Recorded ciphertext stays ciphertext. That is forward secrecy, and it "
              "is one of the properties the published proofs cover."),
        ("h2", "Why a small codebase is a safety feature"),
        ("p", "Proofs cover the design. Code review covers the implementation, and the implementation "
              "is small enough that it has actually been reviewed: a few thousand lines, accepted "
              "into the Linux kernel after scrutiny from the people who maintain it. Bugs in "
              "cryptographic software historically live in the parts nobody read. WireGuard has very "
              "few parts nobody read."),
        ("p", "Size also changes what a bug can be. A protocol that negotiates between dozens of "
              "cipher suites can be tricked into choosing a weak one; several well-known attacks on "
              "older VPN and TLS stacks worked exactly that way. WireGuard has one suite and no "
              "negotiation, so that whole class of attack has nothing to attack. If one of its "
              "primitives is ever broken, the fix is a new protocol version, not a configuration "
              "flag that some servers forget to set."),
        ("h2", "What \"safe\" does not cover"),
        ("p", "A tunnel protects the path, not the endpoints. WireGuard does nothing about a "
              "malicious app on your phone, a phishing page you log in to, or a website that already "
              "knows who you are because you signed in. It also does not hide your traffic from the "
              "VPN server, which decrypts it in order to send it onward. Anyone who tells you a VPN "
              "protocol makes you safe online, full stop, is selling something. It makes one specific "
              "thing safe: the wire between you and a server you chose."),
        ("qa", "What are the downsides of using WireGuard VPN?",
         "Five, and the project lists them itself. It does not disguise its traffic, so an observer "
         "can tell you are using a VPN. Its cryptography is fixed rather than negotiated, which is "
         "safer but means an upgrade needs a new version, not a setting. It needs keys managed for "
         "it, which is why a consumer app has to do that for you. It is not post-quantum by default. "
         "And while you are connected, the server holds your current address in memory, because it "
         "must send packets back."),
        ("p", f'Each of these is on the <a href="{WG_KNOWN_LIMITS}">Known Limitations page</a>. The '
              f'last one deserves a plain sentence: any VPN server knows where to send your packets '
              f'while you are connected. WireGuard neither adds to that nor removes it; the question '
              f'is only whether the operator writes it down, and for how long.'),
        ("qa", "Is WireGuard compromised?",
         "No. There is no known break of the protocol, and the design has published proofs behind "
         "it. When a VPN using WireGuard is compromised, the failure is at the operator: a server "
         "that logs more than it says, a company that sells traffic, a key that was handled badly. "
         "The protocol cannot protect you from the people running it."),
        ("qa", "Which is safer, WireGuard or OpenVPN?",
         "Both are sound when configured well, and neither has a known break. WireGuard is smaller "
         "to audit, fixes its cryptography to modern choices, and has formal proofs; OpenVPN is older, "
         "far larger, more configurable, and can be made to look like ordinary HTTPS traffic, which "
         "WireGuard cannot. For a phone, where battery and reconnecting on the move matter, "
         "WireGuard is the better fit. For hiding that a VPN is in use at all, OpenVPN has a tool "
         "WireGuard lacks."),
        ("h2", "The risk that matters: the operator"),
        ("p", "Everything above is about the tunnel. The tunnel ends at a server, and the server "
              "decrypts your traffic, because that is what sending it onward requires. So the safety "
              "question you can actually act on is not \"is WireGuard safe\" but \"what does this "
              "operator keep\". A protocol with proofs behind it carries traffic to a company you "
              "still have to judge."),
        ("p", "NetCloak's answer is short enough to quote in full, and it is the same paragraph on "
              "every page and in the privacy policy:"),
        ("keep",),
        ("p", "The field-by-field version, including what the server holds while a session runs and "
              "who else touches data, is on the <a href=\"/transparency/\">transparency page</a>. "
              "Read that before you trust any VPN, this one included."),
    ],
}

ARTICLES["/blog/how-netcloak-stays-free/"] = {
    "title": "How a free VPN stays free, and what that costs you · NetCloak VPN",
    "desc": ("Free VPNs are paid for in one of three ways. Which one NetCloak uses, exactly what the "
             "ad company receives, why sessions are timed instead of capped, and what you give up."),
    "eyebrow": "Free, explained",
    "h1": "How a free VPN stays free, and what that costs you",
    "lede": ("Servers cost money. When a VPN charges nothing, someone is paying, and you deserve to "
             "know who. Here is the arithmetic for NetCloak, ad company and all."),
    "published": "2026-09-19",
    "og": ("Free, explained", "How a free VPN\nstays free, and\nwhat it costs you.",
           "Three ways free VPNs are paid for. Which one\nwe use, and exactly what the ad company gets."),
    "body": [
        ("p", "Every free VPN is paid for in one of three ways: by selling what it learns about you, "
              "by using the free tier to sell you a paid one, or by showing you ads. NetCloak is paid "
              "for by ads, specifically rewarded video ads you watch to extend a timed session. What "
              "follows is what that means in practice, what the ad company can and cannot see, and "
              "what it costs you in minutes, speed and choice."),
        ("h2", "The three ways, and what each means for you"),
        ("ul", [
            "<strong>Selling data or traffic.</strong> The VPN logs what you do, or rents out your "
            "connection as an exit for other people's traffic, and sells the result. You pay with "
            "the very thing you installed a VPN to protect. This is the model the warnings about "
            "free VPNs are really about.",
            "<strong>Upselling a paid tier.</strong> The free version is deliberately limited, by "
            "data cap, by speed, by server choice, so that the paid version looks better. Honest, "
            "and common, and it means the free tier is designed to disappoint you eventually.",
            "<strong>Ads.</strong> An advertising network pays the operator to show you ads, and the "
            "service is the same for everyone. You pay in attention. What the ad network learns "
            "about you depends entirely on what the app hands it, which is the part worth reading "
            "closely.",
        ]),
        ("h2", "What the warnings get right, and what they leave out"),
        ("p", f'The pages that rank for "are free VPNs safe" say, roughly, that ads mean data '
              f'sharing. <a href="{PROTON_FREE_MONEY}">Proton\'s piece</a> lists targeting you with '
              f'ads first among the ways free VPNs make money; <a href="{NORTON_FREE_SAFE}">Norton\'s'
              f'</a> cites a study of free Android VPN apps as the reason to be careful. They are '
              f'right that an ad-funded app hands something to an ad company. They leave out what, '
              f'and that is the whole difference.'),
        ("p", f'NetCloak uses Google AdMob. When an ad is requested, AdMob receives the device\'s '
              f'advertising ID, which Android lets you '
              f'<a href="{PLAY_AD_ID_HELP}">reset or delete at any time</a>, along with the ordinary '
              f'facts any app request carries, such as the device model and your public address at '
              f'that moment. What AdMob does not receive is anything from inside the VPN tunnel. The '
              f'ad library runs beside the tunnel, not in it; it has no view of the sites you visit '
              f'through NetCloak, and neither do we, because the traffic is encrypted end to end '
              f'between your phone and the server. An ad company that gets your advertising ID is an '
              f'ordinary ad-funded app. An ad company that gets your browsing would be the first '
              f'model above wearing the third\'s clothes, and it is not what happens here.'),
        ("h2", "Time, not data: why the unit matters"),
        ("p", "Most free VPNs meter data: two gigabytes a month, ten, whatever the tier allows. You "
              "cannot see a data cap coming. A page loads, a video buffers, and somewhere a counter "
              "you never look at runs out. NetCloak meters time instead. You pick a mode before you "
              "connect, and the app shows a clock:"),
        ("modes",),
        ("p", "A clock is honest in a way a cap is not. You know what forty minutes is. You can plan "
              "around it, and when it runs low the app warns you at fifteen percent and again at "
              "five. Watching a rewarded video adds another block of your mode's length, up to a "
              "ceiling of three hours remaining, and if the ceiling means an extension adds less than "
              "a full block, or nothing, the app says so instead of playing the ad and shrugging. How "
              "often an ad is required is a setting we control remotely, and it can be zero; there "
              "have been stretches where no ad was required at all."),
        ("h2", "What it costs you"),
        ("ul", [
            "<strong>Minutes.</strong> A rewarded video is short, but it is your attention, and you "
            "will watch one every time you extend.",
            "<strong>One server.</strong> Ads pay for one server, in New York. If you are far from "
            "it, your traffic travels far. There is no region picker because there is nothing to "
            "pick.",
            "<strong>Speed on the longest mode.</strong> Marathon buys eighty minutes by running at "
            "the base speed. Sprint runs at four times that and lasts twenty. That is the trade, "
            "stated on the tile before you choose it.",
        ]),
        ("h2", "What it does not cost you"),
        ("ul", [
            "<strong>An account.</strong> There is none. No email, no password, nothing to leak.",
            "<strong>Your browsing.</strong> Not logged, not readable, not sold.",
            "<strong>A surprise.</strong> The clock is on the screen the whole time.",
        ]),
        ("h2", "What Google Play requires of a VPN, in plain words"),
        ("p", f'Google\'s <a href="{PLAY_VPN_POLICY}">policy for VPN apps</a> requires an app that '
              f'uses Android\'s VpnService to say so in its listing, to encrypt traffic from the '
              f'device to the tunnel endpoint, and never to make money by redirecting or manipulating '
              f'other apps\' traffic. NetCloak does the first two and does not do the third. The ads '
              f'are ads on a screen, not something done to your traffic.'),
        ("qa", "Can I trust a free VPN?",
         "Trust the one that tells you what it keeps, for how long, and who else is paid, and then "
         "check that the app matches the words. Distrust any free VPN, this one included, that "
         "answers with adjectives instead."),
        ("qa", "Is there a 100% free VPN?",
         "Yes, in the sense that NetCloak never asks for money and has no paid tier. It is paid for "
         "by ads, and the limit is a clock you can see, not a cap you cannot."),
        ("h2", "What we keep"),
        ("keep",),
        ("p", "The field-by-field version is on the <a href=\"/transparency/\">transparency page</a>, "
              "and the session mechanics, including every reason a session can end early, are on "
              "<a href=\"/how-it-works/\">how it works</a>."),
    ],
}
