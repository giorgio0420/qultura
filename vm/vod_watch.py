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
    """List a channel's most recent uploads - just id and link, nothing downloaded.

    --flat-playlist is a lightweight listing: it reliably has id/webpage_url
    but often leaves title/upload_date empty ("NA"), so those two are fetched
    for real below, at download time, from the single-video extraction.
    """
    result = subprocess.run([
        "yt-dlp", "--flat-playlist", "--playlist-end", str(SCAN),
        "--print", "%(id)s\t%(webpage_url)s",
        f"https://www.youtube.com/{handle}/videos",
    ], check=True, capture_output=True, text=True)
    for line in result.stdout.splitlines():
        video_id, link = line.split("\t")
        yield video_id, link


def download_audio(link, out_dir):
    """Download the audio and return (path, title, upload_date) from the same
    full single-video extraction - unlike --flat-playlist, this always has both."""
    result = subprocess.run([
        "yt-dlp", "-f", "bestaudio/best", "--extract-audio", "--audio-format", "mp3",
        "-o", str(out_dir / "audio.%(ext)s"),
        "--print", "after_move:%(title)s\t%(upload_date)s",
        link,
    ], check=True, capture_output=True, text=True)
    title, upload_date = result.stdout.strip().splitlines()[-1].split("\t")
    return next(out_dir.glob("audio.*")), title, upload_date


def main():
    STATE.mkdir(parents=True, exist_ok=True)
    for ch in CHANNELS:
        done_path = STATE / f"vod_{ch['handle'].lstrip('@')}.done"
        done = set(done_path.read_text().split()) if done_path.exists() else set()
        print(f"[vod] checking {ch['name']}...", flush=True)

        new_count = 0
        for video_id, link in recent_videos(ch["handle"]):
            if new_count >= MAX_NEW_PER_RUN:
                break
            if video_id in done:
                continue
            print(f"[vod] {ch['name']}: {video_id}, scaricando...", flush=True)
            try:
                with tempfile.TemporaryDirectory() as tmp:
                    audio_path, title, upload_date = download_audio(link, Path(tmp))
                    text = transcribe(str(audio_path), language=ch.get("lang", "it"))
                published = datetime.strptime(upload_date, "%Y%m%d").replace(tzinfo=timezone.utc)
                push_transcript(ch["queue_dir"], video_id, title, link,
                                 published.isoformat(), text)
                with done_path.open("a") as f:
                    f.write(video_id + "\n")
                new_count += 1
                print(f"[vod] {ch['name']}: {title} pushed.", flush=True)
            except Exception as err:
                print(f"[vod] {ch['name']}: {video_id} FALLITO "
                      f"({type(err).__name__}: {err}) - riprovo al prossimo giro",
                      flush=True)


if __name__ == "__main__":
    main()
