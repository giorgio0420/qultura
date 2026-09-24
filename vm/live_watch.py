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
import time
import traceback
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def _ts():
    return datetime.now().astimezone().isoformat(timespec="seconds")

from common import REPO, push_transcript, transcribe
from ingest import channel_id

CHANNEL_HANDLE = os.environ.get("CHANNEL_HANDLE", "@cronachedispogliatoio")
QUEUE_DIR = os.environ.get("QUEUE_DIR", "yt_transcripts/cronache")
ARCHIVE = REPO / "vm" / "state" / "live_archive.txt"
# Not a tempdir: --live-from-start postprocessing (moov-atom fixup on long DASH
# audio) sometimes fails after a 2-3h download, and a tempdir would delete that
# audio on the way out via the exception. Keeping it here means a failed run
# leaves the raw download behind for inspection/retry instead of losing it.
PENDING_DIR = REPO / "vm" / "state" / "pending"

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
    print(f"[live] {_ts()} {title} ({video_id}) started, downloading...", flush=True)

    PENDING_DIR.mkdir(parents=True, exist_ok=True)
    out_template = PENDING_DIR / f"{video_id}.%(ext)s"
    # Real extension, not a forced .opus: format 140 (this channel's bestaudio)
    # is m4a, and naming it .opus made yt-dlp insert an extra FixupM4a remux
    # before the live-concat FixupDuplicateMoov one - one less thing to fail.
    subprocess.run([
        "yt-dlp", "--no-part", "--live-from-start",
        "-f", "bestaudio/best", "-o", str(out_template), link,
    ], check=True)
    audio_path = next(PENDING_DIR.glob(f"{video_id}.*"))

    print(f"[live] {_ts()} {title} download done, transcribing...", flush=True)
    text = transcribe(audio_path)

    push_transcript(QUEUE_DIR, video_id, title, link,
                     datetime.now(timezone.utc).isoformat(), text)
    mark_done(video_id)
    audio_path.unlink()
    print(f"[live] {_ts()} {title} pushed.", flush=True)


def main():
    api_key = os.environ["YOUTUBE_API_KEY"]
    cid = channel_id(CHANNEL_HANDLE)
    print(f"[live] {_ts()} === SESSION START pid={os.getpid()} === "
          f"watching {CHANNEL_HANDLE} ({cid}), polling every {POLL_SECONDS}s",
          flush=True)
    archive = load_archive()
    while True:
        try:
            item = is_live(cid, api_key)
            if item and item["id"]["videoId"] not in archive:
                handle_live(item)
                archive = load_archive()
        except KeyboardInterrupt:
            print(f"[live] {_ts()} === SESSION END: interrupted (Ctrl+C / stop) ===",
                  flush=True)
            raise
        except Exception:
            print(f"[live] {_ts()} error during poll/download cycle:", flush=True)
            traceback.print_exc()
            leftover = list(PENDING_DIR.glob("*")) if PENDING_DIR.exists() else []
            if leftover:
                print(f"[live] {_ts()} raw audio kept for recovery: "
                      f"{', '.join(str(p) for p in leftover)}", flush=True)
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
