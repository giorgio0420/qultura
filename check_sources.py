"""Health check for sources.json: does every feed still answer? Run it when a
category goes quiet. Usage: python check_sources.py"""

import concurrent.futures
import socket

import feedparser

from ingest import SOURCES, channel_id

socket.setdefaulttimeout(30)


def check(src):
    try:
        url = (src["url"] if src["kind"] == "rss" else
               "https://www.youtube.com/feeds/videos.xml?channel_id="
               + channel_id(src["url"]))
        entries = feedparser.parse(url).entries
    except Exception as e:
        return False, f"FAIL {src['name']}: {type(e).__name__}"
    latest = entries[0].get("title", "")[:50] if entries else "(no entries)"
    return bool(entries), f"{'ok  ' if entries else 'EMPTY'} {src['name']:<34} {latest}"


if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(8) as ex:
        results = list(ex.map(check, SOURCES))
    for _, line in results:
        print(line)
    bad = sum(1 for ok, _ in results if not ok)
    print(f"\n{len(results) - bad}/{len(results)} sources alive")
