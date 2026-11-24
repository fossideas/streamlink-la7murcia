"""
$description Live TV channel "La 7" (Región de Murcia, Spain), streamed through the Globalmest platform.
$url la7tv.es
$url rtv-murcia-live.globalmest.com
$type live
$metadata title
$region Spain
"""

import logging
import re
from urllib.parse import parse_qsl, urlparse

from streamlink.plugin import Plugin, PluginError, pluginmatcher
from streamlink.stream.hls import HLSStream
from streamlink.utils.url import update_qsd


log = logging.getLogger(__name__)

# Header/param name used by the MEST player to authenticate every request
TOKEN_HEADER = "auth-token"
TOKEN_PARAM = "auth_token"

# The page that embeds the player and hands out a (short-lived) token
LIVE_PAGE_URL = "https://www.la7tv.es/a-la-carta/7tv-en-directo/20220810150726000939.html"
DEFAULT_HLS_URL = "https://rtv-murcia-live.globalmest.com/principal/smil:principal.smil/playlist.m3u8"

_JWT = r"eyJ[\w-]+\.[\w-]+\.[\w-]+"
_TOKEN_REGEXES = (
    # <script src=".../Q3zG7J.js?token=JWT"> (player embed, token generated server-side)
    re.compile(rf"""globalmest\.[a-z]+/[^"'\s>]+\.js\?[^"'\s>]*?token=(?P<token>{_JWT})"""),
    # <source src=".../playlist.m3u8?auth_token=JWT"> (already rendered player)
    re.compile(rf"auth_token=(?P<token>{_JWT})"),
    # any other ?token=JWT / &token=JWT
    re.compile(rf"[?&;]token=(?P<token>{_JWT})"),
)
_HLS_REGEX = re.compile(r"""(?P<url>https?://[\w.-]+\.globalmest\.com/[^"'\s<>?]+\.m3u8)""")


@pluginmatcher(
    name="page",
    pattern=re.compile(r"https?://(?:www\.)?la7tv\.es/"),
)
@pluginmatcher(
    name="hls",
    pattern=re.compile(r"https?://rtv-murcia-live\.globalmest\.com/.+\.m3u8"),
)
class La7TV(Plugin):
    def _fetch_page(self):
        return self.session.http.get(
            LIVE_PAGE_URL if self.matches["hls"] else self.url,
            headers={"Referer": "https://www.la7tv.es/"},
        ).text

    @staticmethod
    def _find_token(html):
        for regex in _TOKEN_REGEXES:
            m = regex.search(html)
            if m:
                return m.group("token")
        return None

    def _get_streams(self):
        self.title = "La 7 TV Directo"

        hls_url = None
        token = None

        if self.matches["hls"]:
            # a full URL copied from the browser already carries the token
            hls_url = self.url
            token = dict(parse_qsl(urlparse(self.url).query)).get(TOKEN_PARAM)
            html = None if token else self._fetch_page()
        else:
            html = self._fetch_page()

        if html is not None:
            token = self._find_token(html)
            if not hls_url:
                m = _HLS_REGEX.search(html)
                hls_url = m.group("url") if m else DEFAULT_HLS_URL

        if not token:
            raise PluginError("Could not find the authentication token in the page")

        log.debug(f"Using HLS URL: {hls_url}")
        hls_url = update_qsd(hls_url, {TOKEN_PARAM: token})

        # The web player also sends the token as a header on every
        # playlist and segment request, so do the same.
        return HLSStream.parse_variant_playlist(
            self.session,
            hls_url,
            headers={
                TOKEN_HEADER: token,
                "Origin": "https://www.la7tv.es",
                "Referer": "https://www.la7tv.es/",
            },
        )


__plugin__ = La7TV
