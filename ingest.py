"""Fetch raw text from every configured source. No AI, no persistence here."""

import json
import re
import sys
import time
import urllib.request
from datetime import datetime, timedelta, timezone

import feedparser
import trafilatura
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import IpBlocked, RequestBlocked

# kind "rss" -> url is a feed URL; kind "yt" -> url is a UC... channel id (or @handle).
# Optional keys: out_lang (curation output language), lang (transcript languages),
# match (keep only items whose title/text contains this word), handle (documentation).
with open("sources.json", encoding="utf-8") as f:
    SOURCES = json.load(f)

UA = {"User-Agent": "Mozilla/5.0"}
MIN_TRANSCRIPT = 500  # chars: below this it is a short or a teaser, not substance
MIN_RSS = 800  # many feeds ship only an excerpt; below this, fetch the article itself
MAX_AGE_DAYS = 7  # a weekly podcast still qualifies; `seen` stops repeat downloads
TRANSCRIPT_PAUSE = 2  # seconds between transcript requests, to stay under YouTube's radar

# YouTube blocks the whole IP once it decides we are scraping, and every later request
# in the same run then fails anyway. Give up on video for the rest of the run instead.
# ponytail: process-global flag, fine for a single-threaded daily script.
_blocked = False


def channel_id(handle):
    """Resolve a @handle to a UC... channel id by reading the channel page."""
    if handle.startswith("UC"):
        return handle
    req = urllib.request.Request(f"https://www.youtube.com/{handle}", headers=UA)
    html = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "ignore")
    m = re.search(r'youtube\.com/channel/(UC[\w-]{22})', html)
    if not m:
        raise LookupError(f"channel id not found for {handle}")
    return m.group(1)


def strip_html(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def fetch_rss(source, seen=(), limit=3):
    """Yield (title, link, text) for the latest entries of an RSS feed."""
    for e in feedparser.parse(source["url"]).entries[:source.get("limit", limit)]:
        body = e["content"][0].get("value", "") if e.get("content") else ""
        title, link = e.get("title", ""), e.get("link", "")
        if link in seen:
            continue
        text = strip_html(body or e.get("summary", ""))
        if len(text) < MIN_RSS and link:
            text = article_text(link) or text
        if not keep(source, title, text):
            continue
        yield title, link, text


def article_text(url):
    """Full article body for feeds that publish only an excerpt."""
    try:
        return trafilatura.extract(trafilatura.fetch_url(url))
    except Exception as err:
        print(f"  [skip] {url}: {type(err).__name__}", file=sys.stderr)
        return None


def fetch_youtube(source, seen=(), limit=2, scan=15):
    """Yield up to `limit` (title, link, transcript) from a channel's recent uploads.

    Shorts, videos older than MAX_AGE_DAYS and videos without a usable transcript are
    skipped. Once YouTube blocks the IP, stop asking for the rest of the run.
    """
    global _blocked
    if _blocked:
        return
    feed = feedparser.parse("https://www.youtube.com/feeds/videos.xml?channel_id="
                            + channel_id(source["url"]))
    api = YouTubeTranscriptApi()
    cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)
    kept = 0
    for e in feed.entries[:scan]:
        if kept >= limit:
            return
        link = e.get("link", "")
        if link in seen or "/shorts/" in link or published(e) < cutoff:
            continue  # skipping before the request is what keeps the daily count low
        time.sleep(TRANSCRIPT_PAUSE)
        try:
            snippets = api.fetch(e.yt_videoid, languages=source.get("lang", ["it", "en"]))
        except (IpBlocked, RequestBlocked):
            _blocked = True
            print("  [skip] YouTube blocked this IP, skipping video for this run",
                  file=sys.stderr)
            return
        except Exception as err:  # captions disabled, age gate, unplayable
            print(f"  [skip] {e.yt_videoid}: {type(err).__name__}", file=sys.stderr)
            continue
        text = " ".join(s.text for s in snippets)
        title = e.get("title", "")
        if len(text) < MIN_TRANSCRIPT or not keep(source, title, text):
            continue
        kept += 1
        yield title, link, text


def published(entry):
    """Publication time of a feed entry, or the epoch when the feed omits it."""
    t = entry.get("published_parsed") or entry.get("updated_parsed")
    return (datetime(*t[:6], tzinfo=timezone.utc) if t
            else datetime.min.replace(tzinfo=timezone.utc))


def keep(source, title, text):
    """Apply the source's optional keyword filter (for broad, off-topic feeds).

    Matched on the title only: a passing mention in the body is not what the filter
    is for, and word boundaries keep "roma" from matching "Romania".
    """
    word = source.get("match")
    return not word or re.search(rf"{re.escape(word)}", title, re.I) is not None


def fetch(source, seen=()):
    """Yield the source's new content. `seen` holds links already curated, so their
    transcript or article is never downloaded twice."""
    grab = fetch_rss if source["kind"] == "rss" else fetch_youtube
    return grab(source, seen)


if __name__ == "__main__":
    for src in SOURCES:
        print(f"\n=== {src['name']} ({src['kind']}) ===")
        for title, link, text in fetch(src):
            print(f"- {title} | {link}\n  chars={len(text)}")
