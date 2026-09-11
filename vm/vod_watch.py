"""Periodic worker: pull new uploads from a list of channels and transcribe them.

Run via cron (e.g. every 3 hours - see setup.sh). Each channel keeps its own
DONE file under vm/state/, written to only *after* a video is transcribed and
pushed successfully - not yt-dlp's own --download-archive, which would mark a
video done the moment its download finishes, before transcription even starts.
With many channels sharing Groq's free-tier daily audio quota, a transcription
can fail (quota exhausted) after a clean download; keeping our own DONE file
means that video is simply retried on the next run instead of being silently
skipped forever.

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
SCAN = 8  # how many recent uploads to check per channel before giving up


def recent_videos(handle):
    """List a channel's most recent uploads - metadata only, nothing downloaded."""
    result = subprocess.run([
        "yt-dlp", "--flat-playlist", "--playlist-end", str(SCAN),
        "--print", "%(id)s\t%(title)s\t%(webpage_url)s\t%(upload_date)s",
        f"https://www.youtube.com/{handle}/videos",
    ], check=True, capture_output=True, text=True)
    for line in result.stdout.splitlines():
        video_id, title, link, upload_date = line.split("\t")
        yield video_id, title, link, upload_date


def download_audio(link, out_dir):
    subprocess.run([
        "yt-dlp", "-f", "bestaudio/best", "--extract-audio", "--audio-format", "mp3",
        "-o", str(out_dir / "audio.%(ext)s"), link,
    ], check=True)
    return next(out_dir.glob("audio.*"))


def main():
    STATE.mkdir(parents=True, exist_ok=True)
    for ch in CHANNELS:
        done_path = STATE / f"vod_{ch['handle'].lstrip('@')}.done"
        done = set(done_path.read_text().split()) if done_path.exists() else set()
        print(f"[vod] checking {ch['name']}...", flush=True)

        new_count = 0
        for video_id, title, link, upload_date in recent_videos(ch["handle"]):
            if new_count >= MAX_NEW_PER_RUN:
                break
            if video_id in done:
                continue
            print(f"[vod] {ch['name']}: {title} ({video_id}), scaricando...", flush=True)
            try:
                with tempfile.TemporaryDirectory() as tmp:
                    audio_path = download_audio(link, Path(tmp))
                    text = transcribe(str(audio_path), language=ch.get("lang", "it"))
                published = datetime.strptime(upload_date, "%Y%m%d").replace(tzinfo=timezone.utc)
                push_transcript(ch["queue_dir"], video_id, title, link,
                                 published.isoformat(), text)
                with done_path.open("a") as f:
                    f.write(video_id + "\n")
                new_count += 1
                print(f"[vod] {ch['name']}: {title} pushed.", flush=True)
            except Exception as err:
                print(f"[vod] {ch['name']}: {title} FALLITO "
                      f"({type(err).__name__}: {err}) - riprovo al prossimo giro",
                      flush=True)


if __name__ == "__main__":
    main()
