#!/usr/bin/env python3
"""
Get the tokenised HLS URL of "La 7 TV Directo" (https://www.la7tv.es).

How the site works (from the saved HTML/JS):
  * The page embeds a MEST player script (id "Q3zG7J"), whose URL carries
    the token:  .../Q3zG7J.js?token=<JWT>
  * The player code does:   src + "?auth_token=" + token
    and for every playlist/segment request it also sends the header
        auth-token: <JWT>
  * The JWT (HS256, claims: app_key, exp) is signed SERVER-SIDE by the site,
    so it can't be generated locally: it has to be read from the page that the
    site serves. Tokens are short-lived (exp), so fetch a fresh one each time.

Usage:
    python la7_hls_token.py                # print the full m3u8 URL
    python la7_hls_token.py --verify       # also test it against the server
    python la7_hls_token.py --html-file saved_page.html   # parse a saved page
"""
import argparse
import base64
import json
import re
import sys
import time
import urllib.request

PAGE_URL = "https://www.la7tv.es/a-la-carta/7tv-en-directo/20220810150726000939.html"
BASE_M3U8 = "https://rtv-murcia-live.globalmest.com/principal/smil:principal.smil/playlist.m3u8"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

JWT = r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"

# Places where the token can appear in the HTML, in order of preference:
PATTERNS = [
    rf"Q3zG7J\.js\?[^\"'>\s]*?token=({JWT})",   # player <script src="...?token=JWT">
    rf"auth_token=({JWT})",                      # <source src="...m3u8?auth_token=JWT">
    rf"[?&;]token=({JWT})",                      # any other ?token= usage
]


def http_get(url, headers=None, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def decode_jwt(token):
    """Decode the JWT payload (no signature check, just to read 'exp')."""
    payload = token.split(".")[1]
    payload += "=" * (-len(payload) % 4)
    return json.loads(base64.urlsafe_b64decode(payload))


def extract_token(html):
    for pat in PATTERNS:
        m = re.search(pat, html)
        if m:
            return m.group(1)
    return None


def get_token(page_url=PAGE_URL, html_file=None):
    if html_file:
        with open(html_file, encoding="utf-8", errors="replace") as f:
            html = f.read()
    else:
        html = http_get(page_url, {"Referer": "https://www.la7tv.es/"})
    token = extract_token(html)
    if not token:
        raise RuntimeError(
            "Token not found in the page. The site may have changed, or the "
            "token is injected by a request not present in the static HTML "
            "(check the Network tab for 'Q3zG7J.js?token=' or 'auth_token=')."
        )
    return token


def verify(url, token):
    """Request the playlist like the player does (auth_token in URL + header)."""
    body = http_get(url, {
        "auth-token": token,
        "Origin": "https://www.la7tv.es",
        "Referer": "https://www.la7tv.es/",
    })
    ok = body.lstrip().startswith("#EXTM3U")
    print(f"[verify] playlist {'OK' if ok else 'UNEXPECTED RESPONSE'} "
          f"({len(body)} bytes)", file=sys.stderr)
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--page", default=PAGE_URL, help="page that embeds the player")
    ap.add_argument("--html-file", help="parse a locally saved HTML instead of downloading")
    ap.add_argument("--verify", action="store_true", help="test the URL against the server")
    ap.add_argument("--token-only", action="store_true", help="print only the JWT")
    args = ap.parse_args()

    token = get_token(args.page, args.html_file)
    try:
        exp = decode_jwt(token).get("exp")
        if exp:
            left = int(exp - time.time())
            print(f"[info] token expires in {left // 60} min "
                  f"({time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(exp))})",
                  file=sys.stderr)
    except Exception:
        pass

    url = f"{BASE_M3U8}?auth_token={token}"
    if args.verify:
        verify(url, token)
    print(token if args.token_only else url)


if __name__ == "__main__":
    main()
