"""Periodic worker: pull new uploads from a list of channels and transcribe them.

Run via cron (e.g. every 3 hours - see setup.sh). Each channel keeps its own
yt-dlp --download-archive file under vm/state/, so a video is downloaded once
ever, independent of whether GitHub Actions later deletes its queue file from
the repo.

    python vm/vod_watch.py
"""

import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from common import REPO, push_transcript, transcribe

CHANNELS = json.loads((Path(__file__).parent / "vod_channels.json").read_text())
STATE = REPO / "vm" / "state"
MAX_NEW_PER_RUN = 3  # mirrors ingest.py's own per-source fetch limits


def new_uploads(handle, archive_path):
    """Download up to MAX_NEW_PER_RUN new uploads' audio, yield (meta, path)."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        result = subprocess.run([
            "yt-dlp", "--download-archive", str(archive_path),
            "--playlist-end", str(MAX_NEW_PER_RUN),
            "-f", "bestaudio/best", "--extract-audio", "--audio-format", "mp3",
            "-o", str(tmp / "%(id)s.%(ext)s"),
            "--print", "after_move:%(id)s\t%(title)s\t%(webpage_url)s\t%(upload_date)s",
            f"https://www.youtube.com/{handle}/videos",
        ], check=True, capture_output=True, text=True)

        for line in result.stdout.splitlines():
            video_id, title, link, upload_date = line.split("\t")
            audio_path = next(tmp.glob(f"{video_id}.*"))
            yield video_id, title, link, upload_date, audio_path
            audio_path.unlink(missing_ok=True)


def main():
    STATE.mkdir(parents=True, exist_ok=True)
    for ch in CHANNELS:
        archive = STATE / f"vod_{ch['handle'].lstrip('@')}.txt"
        print(f"[vod] checking {ch['name']}...", flush=True)
        for video_id, title, link, upload_date, audio_path in new_uploads(ch["handle"], archive):
            print(f"[vod] {ch['name']}: {title} ({video_id}), transcribing...", flush=True)
            text = transcribe(audio_path, language=ch.get("lang", "it"))
            published = datetime.strptime(upload_date, "%Y%m%d").replace(tzinfo=timezone.utc)
            push_transcript(ch["queue_dir"], video_id, title, link,
                             published.isoformat(), text)
            print(f"[vod] {ch['name']}: {title} pushed.", flush=True)


if __name__ == "__main__":
    main()
