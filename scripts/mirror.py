#!/usr/bin/env python3
"""Faithful static mirror of archaeasoftware.com -> Cloudflare-ready static site."""
import os, re, sys, urllib.request, urllib.parse

BASE = "https://archaeasoftware.com"
OUT = sys.argv[1]
UA = {"User-Agent": "Mozilla/5.0 (mirror)"}
PAGES = {"/": "index.html", "/about/": "about/index.html"}

def fetch(url, binary=False):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    return data if binary else data.decode("utf-8")

def save(path, data, binary=False):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    mode = "wb" if binary else "w"
    with open(full, mode, **({} if binary else {"encoding": "utf-8"})) as f:
        f.write(data)

def strip_junk(html):
    rules = [
        # RSS / comment feeds
        r'<link rel="alternate" type="application/rss\+xml"[^>]*>\s*',
        # WP REST API discovery, RSD/EditURI, wlwmanifest, pingback, shortlink
        r'<link rel="https://api\.w\.org/"[^>]*>\s*',
        r'<link rel="EditURI"[^>]*>\s*',
        r'<link rel="wlwmanifest"[^>]*>\s*',
        r'<link rel="pingback"[^>]*>\s*',
        r'<link rel="shortlink"[^>]*>\s*',
        # oEmbed discovery (attribute order varies; json+oembed and text/xml+oembed)
        r'<link[^>]*oembed[^>]*>\s*',
        # any REST API discovery link (wp-json), regardless of quoting/order
        r'<link[^>]*wp-json[^>]*>\s*',
        # shortlink (?p=N), single- or double-quoted
        r"<link[^>]*rel=['\"]shortlink['\"][^>]*>\s*",
        # generator fingerprint
        r'<meta name="generator"[^>]*>\s*',
        # emoji: inline style, settings json, and the auto-generated loader module
        r'<style id="wp-emoji-styles-inline-css">.*?</style>\s*',
        r'<script id="wp-emoji-settings"[^>]*>.*?</script>\s*',
    ]
    for pat in rules:
        html = re.sub(pat, "", html, flags=re.S)
    # remove the emoji loader <script type="module"> ... wp-emoji-settings ... </script>
    html = re.sub(
        r'<script type="module">\s*/\*! This file is auto-generated \*/.*?</script>\s*',
        "", html, flags=re.S)
    return html

def collect_assets(html):
    urls = set(re.findall(r'https?://archaeasoftware\.com/(?:wp-content|wp-includes)/[^"\')\s]+', html))
    return urls

def local_path(asset_url):
    p = urllib.parse.urlparse(asset_url).path  # drops query string
    return p.lstrip("/")  # e.g. wp-content/uploads/2024/12/Archaea_A.jpg

# Literal internal-page link normalizations (assets handled separately).
PAGE_LINKS = {
    'href="https://archaeasoftware.com/"': 'href="/"',
    "href='https://archaeasoftware.com/'": "href='/'",
    'href="https://archaeasoftware.com"': 'href="/"',
    'href="http://archaeasoftware.com/about/"': 'href="/about/"',
    'href="http://archaeasoftware.com/about"': 'href="/about/"',
    'href="https://archaeasoftware.com/about/"': 'href="/about/"',
    'href="https://archaeasoftware.com/about"': 'href="/about/"',
}

all_assets = {}
for route, dest in PAGES.items():
    print(f"[fetch] {route}")
    html = fetch(BASE + route)
    html = strip_junk(html)
    for au in collect_assets(html):
        all_assets[au] = local_path(au)
    # rewrite asset URLs -> root-relative, query stripped
    for au, lp in sorted(all_assets.items(), key=lambda x: -len(x[0])):
        html = html.replace(au, "/" + lp)
    # normalize internal page links
    for a, b in PAGE_LINKS.items():
        html = html.replace(a, b)
    save(dest, html)
    print(f"  -> {dest} ({len(html)} bytes)")

print(f"[assets] {len(all_assets)} unique")
for au, lp in sorted(all_assets.items()):
    data = fetch(au, binary=True)
    save(lp, data, binary=True)
    print(f"  {lp} ({len(data)} bytes)")
print("DONE")
