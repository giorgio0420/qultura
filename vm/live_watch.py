"""Long-running worker: watches one channel and transcribes it while live.

Run as a systemd service (see qultura-live.service). Polls the YouTube Data
API v3 for live status, downloads audio with yt-dlp while the stream runs
(--live-from-start blocks until the broadcast ends), transcribes it with
Whisper, and pushes the transcript into the qultura repo as a queue file.

No YouTube login: the stream's audio is public, yt-dlp needs no cookies.

    YOUTUBE_API_KEY=...        python vm/live_watch.py

Env vars (see vm/.env):
    YOUTUBE_API_KEY   Google Cloud API key with "YouTube Data API v3" enabled.
    CHANNEL_HANDLE    e.g. @cronachedispogliatoio (default below).
    QUEUE_DIR         path under the repo to drop transcripts in.
"""

import json
import os
import subprocess
import sys
import tempfile
import time
import traceback
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from common import REPO, push_transcript, transcribe
from ingest import channel_id

CHANNEL_HANDLE = os.environ.get("CHANNEL_HANDLE", "@cronachedispogliatoio")
QUEUE_DIR = os.environ.get("QUEUE_DIR", "yt_transcripts/cronache")
ARCHIVE = REPO / "vm" / "state" / "live_archive.txt"

# search.list costs 100 quota units/call against a 10000/day free quota.
# Every 15 min = 96 calls/day, leaving headroom for other API use.
POLL_SECONDS = 900


def is_live(cid, api_key):
    """Return the live video's {id, title, publishedAt}, or None."""
    q = urllib.parse.urlencode({
        "part": "snippet", "channelId": cid, "eventType": "live",
        "type": "video", "key": api_key,
    })
    url = f"https://www.googleapis.com/youtube/v3/search?{q}"
    with urllib.request.urlopen(url, timeout=20) as r:
        items = json.load(r).get("items", [])
    return items[0] if items else None


def load_archive():
    return set(ARCHIVE.read_text().split()) if ARCHIVE.exists() else set()


def mark_done(video_id):
    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    with ARCHIVE.open("a") as f:
        f.write(video_id + "\n")


def handle_live(item):
    video_id = item["id"]["videoId"]
    title = item["snippet"]["title"]
    link = f"https://www.youtube.com/watch?v={video_id}"
    print(f"[live] {title} ({video_id}) started, downloading...", flush=True)

    with tempfile.TemporaryDirectory() as tmp:
        audio_path = Path(tmp) / f"{video_id}.opus"
        # Blocks for the whole stream: yt-dlp keeps appending until it ends.
        subprocess.run([
            "yt-dlp", "--no-part", "--live-from-start",
            "-f", "bestaudio/best", "-o", str(audio_path), link,
        ], check=True)

        print(f"[live] {title} ended, transcribing...", flush=True)
        text = transcribe(audio_path)

    push_transcript(QUEUE_DIR, video_id, title, link,
                     datetime.now(timezone.utc).isoformat(), text)
    mark_done(video_id)
    print(f"[live] {title} pushed.", flush=True)


def main():
    api_key = os.environ["YOUTUBE_API_KEY"]
    cid = channel_id(CHANNEL_HANDLE)
    print(f"[live] watching {CHANNEL_HANDLE} ({cid}), polling every {POLL_SECONDS}s",
          flush=True)
    archive = load_archive()
    while True:
        try:
            item = is_live(cid, api_key)
            if item and item["id"]["videoId"] not in archive:
                handle_live(item)
                archive = load_archive()
        except Exception:
            traceback.print_exc()
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
