# Serverless transform for the Google Photos Album plugin.
#
# A public Google Photos shared album page embeds all of its photo data in one
# or more `AF_initDataCallback({...})` blocks in the HTML. Each photo entry is a
# nested array whose [1] element is [base_url, width, height]. This transform
# fetches the album HTML, parses out those entries, picks a random one, and
# returns its bare base URL; the layout appends a per-device size at render time.
#
# run(input) receives the trmnl namespace (including custom field values) and has
# network access. We fetch the album ourselves (stdlib urllib, no third-party
# deps) rather than relying on the polling step, since Google returns HTML (not
# JSON) and the same code then works both locally (trmnlp) and hosted.

import re
import ssl
import json
import random
import urllib.request

# A desktop UA is required: mobile user-agents get a stripped page without the
# AF_initDataCallback photo data.
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    # Pre-accept the consent gate so Google serves the album page directly
    # instead of an interstitial to server-side (cookie-less) requests.
    "Cookie": "CONSENT=YES+cb",
}

# Fetch resilience. Google occasionally times out or the goo.gl redirect blips;
# retry so one bad poll doesn't blank the screen. Keep timeout * attempts within
# the ~5s serverless budget — a normal fetch is ~0.5s, so 2s is already generous,
# and capping it leaves room for a retry instead of one slow attempt eating it all.
_FETCH_TIMEOUT = 4
_FETCH_ATTEMPTS = 3

# Disable TLS certificate verification for the album fetch.
#
# TRMNL's hosted serverless clock currently lags real time, so when a fetch hits
# a Google server presenting a freshly-rotated certificate, verification fails
# intermittently with "SSLCertVerificationError: certificate is not yet valid".
# We only read PUBLIC album HTML (no credentials, no secrets), so bypassing
# verification is an acceptable stopgap. Set back to False once TRMNL fixes the
# runtime clock and the "not yet valid" errors stop.
_DISABLE_SSL_VERIFY = True


def run(input):
    album_url = _get_field(input, "album_url")
    if not album_url:
        return _error("No album URL configured. Add a public Google Photos album URL in the plugin settings.")

    album_url = album_url.strip()
    try:
        html = _fetch(album_url)
    except Exception as e:  # noqa: BLE001 - surface any fetch error to the screen
        return _error(
            "Could not load the album after %d tries: %s. "
            "Check that the URL is correct and public."
            % (_FETCH_ATTEMPTS, _describe_error(e))
        )

    photos = _parse_photos(html)
    if not photos:
        return _error("No photos found. Make sure the album is shared with 'anyone with the link'.")

    chosen = random.choice(photos)
    return {
        # Bare base URL (no size param). The layout appends a per-device size
        # at render time from trmnl.device.{width,height}, so each device gets a
        # correctly-sized image and larger/future panels stay crisp automatically.
        "image_base": _base_url(chosen["url"]),
        "orig_width": chosen["width"],
        "orig_height": chosen["height"],
        "photo_count": len(photos),
        "error": "",
    }


# --- helpers ----------------------------------------------------------------

def _fetch(url):
    """Fetch album HTML with stdlib urllib, following redirects (incl. the
    photos.app.goo.gl -> photos.google.com/share/... hop).

    Google occasionally times out or the goo.gl short-link redirect blips, which
    would otherwise blank the screen on that poll. Retry a few times so a single
    transient failure doesn't surface as an error."""
    context = _ssl_context()
    last_err = None
    for _ in range(_FETCH_ATTEMPTS):
        try:
            req = urllib.request.Request(url, headers=_HEADERS)
            with urllib.request.urlopen(req, timeout=_FETCH_TIMEOUT, context=context) as resp:
                charset = resp.headers.get_content_charset() or "utf-8"
                return resp.read().decode(charset, errors="replace")
        except Exception as e:  # noqa: BLE001 - retry any transient fetch error
            last_err = e
    raise last_err if last_err is not None else RuntimeError("fetch failed")


def _ssl_context():
    """Unverified TLS context when _DISABLE_SSL_VERIFY is set, else default
    (verified). See _DISABLE_SSL_VERIFY for why this stopgap exists."""
    if not _DISABLE_SSL_VERIFY:
        return None
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context


def _error(message):
    return {"image_base": "", "error": message, "photo_count": 0}


def _describe_error(e):
    """Human-readable, angle-bracket-free description of a fetch error.

    urllib's URLError stores the real cause in .reason and stringifies to
    '<urlopen error ...>' — the angle brackets get swallowed when the message is
    rendered as HTML on the device, so str(e) shows up blank. We unwrap to the
    underlying reason (timeout / ConnectionResetError / gaierror / SSLError), and
    surface HTTPError's status .code (e.g. 429 rate-limited, 403, 5xx) so the
    on-screen error actually says what went wrong."""
    name = type(e).__name__
    code = getattr(e, "code", None)
    if code is not None:  # HTTPError is a URLError subclass with an HTTP status
        return "%s %s" % (name, code)
    reason = getattr(e, "reason", None)
    if isinstance(reason, BaseException):
        rtext = str(reason).strip()
        inner = type(reason).__name__ + (": " + rtext if rtext else "")
    else:
        inner = str(reason).strip() if reason else str(e).strip()
    detail = "%s (%s)" % (name, inner) if inner else name
    return detail.replace("<", "").replace(">", "")


def _get_field(input, name):
    """Find a custom field value by key, regardless of where the runtime nests it."""
    if not isinstance(input, dict):
        return None
    # Known path for both trmnlp and hosted serverless.
    try:
        cfv = input["trmnl"]["plugin_settings"]["custom_fields_values"]
        if isinstance(cfv, dict) and cfv.get(name):
            return cfv[name]
    except (KeyError, TypeError):
        pass
    # Fallback: recursive search for the first matching key.
    return _deep_find(input, name)


def _deep_find(obj, name):
    if isinstance(obj, dict):
        if obj.get(name):
            return obj[name]
        for v in obj.values():
            found = _deep_find(v, name)
            if found:
                return found
    elif isinstance(obj, list):
        for v in obj:
            found = _deep_find(v, name)
            if found:
                return found
    return None


def _parse_photos(html):
    """Extract photo entries from every AF_initDataCallback data array."""
    photos = []
    seen = set()
    for data in _data_arrays(html):
        for entry in _iter_photo_entries(data):
            url, w, h = entry
            if url in seen:
                continue
            seen.add(url)
            photos.append({"url": url, "width": w, "height": h})
    return photos


def _data_arrays(html):
    """Yield each parsed `data:[...]` array found inside AF_initDataCallback(...)."""
    marker = "AF_initDataCallback("
    idx = 0
    while True:
        i = html.find(marker, idx)
        if i == -1:
            return
        i += len(marker)
        idx = i
        end = html.find(");</script>", i)
        block = html[i:end] if end != -1 else html[i:i + 500000]
        m = re.search(r"data\s*:\s*\[", block)
        if not m:
            continue
        arr = _balanced_array(block, m.end() - 1)
        if not arr:
            continue
        try:
            yield json.loads(arr)
        except ValueError:
            continue


def _balanced_array(s, start):
    """Return the JSON array substring starting at index `start` ('['), matching brackets."""
    depth = 0
    in_str = False
    esc = False
    for j in range(start, len(s)):
        c = s[j]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                return s[start:j + 1]
    return None


def _iter_photo_entries(data):
    """Yield (url, width, height) for photo entries anywhere in a data array.

    A photo entry is a list whose [1] element is [url, width, height]. We scan
    every nested list so we don't depend on Google's exact top-level indexing.
    """
    if not isinstance(data, list):
        return
    for top in data:
        if not isinstance(top, list):
            continue
        for entry in top:
            if not isinstance(entry, list) or len(entry) < 2:
                continue
            detail = entry[1]
            if (
                isinstance(detail, list)
                and len(detail) >= 3
                and isinstance(detail[0], str)
                and detail[0].startswith("http")
                and "googleusercontent" in detail[0]
                and isinstance(detail[1], int)
                and isinstance(detail[2], int)
            ):
                yield detail[0], detail[1], detail[2]


def _base_url(base):
    """Return the bare base URL, stripping any trailing size parameter."""
    return re.sub(r"=[-\w]+$", "", base)


# Allow standalone testing: `python transform.py <album_url>`
if __name__ == "__main__":
    import sys

    test_input = {
        "trmnl": {
            "plugin_settings": {
                "custom_fields_values": {
                    "album_url": sys.argv[1] if len(sys.argv) > 1 else "",
                    "display_mode": "fill",
                }
            }
        }
    }
    print(json.dumps(run(test_input), indent=2))
