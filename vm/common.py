"""Shared helpers for the transcription workers running on the VPS.

Both workers live inside a clone of the qultura repo, so they push straight
into it via plain git subprocess calls instead of a REST API or a queue
service - the repo itself is the queue (see ingest.py's fetch_queue).

Transcription runs on Groq's hosted Whisper (whisper-large-v3-turbo), not a
local model: a 1-2 vCPU / 1-2 GB VPS has no business loading Whisper itself
into memory. Groq's free tier caps uploaded files at 25 MB, well under what
even a short live stream's audio would be, so audio is chunked with ffmpeg
before each request.
"""

import os
import pathlib
import subprocess
import sys
import tempfile
import time

import requests

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))


def _load_env():
    """Read vm/.env into os.environ, without overriding what's already set.

    systemd's EnvironmentFile covers this on the VPS; this covers every other
    way the workers get launched (a plain terminal, Windows Task Scheduler)
    without each of those needing its own env-loading step.
    """
    path = REPO / "vm" / ".env"
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip("\"'"))


_load_env()

GROQ_MODEL = "whisper-large-v3-turbo"
CHUNK_SECONDS = 1200  # 20 min at 16kHz mono 32kbps ~= 4.7MB, safely under 25MB


def transcribe(audio_path, language="it"):
    """Return the transcript text for one audio file, via the Groq API.

    Re-encodes to a low-bitrate mono chunk stream first: keeps each upload
    small and keeps yt-dlp's own download format (whatever bestaudio was)
    out of the equation entirely.
    """
    with tempfile.TemporaryDirectory() as tmp:
        pattern = str(pathlib.Path(tmp) / "chunk%03d.mp3")
        subprocess.run([
            "ffmpeg", "-loglevel", "error", "-i", str(audio_path),
            "-ar", "16000", "-ac", "1", "-b:a", "32k",
            "-f", "segment", "-segment_time", str(CHUNK_SECONDS), pattern,
        ], check=True)
        chunks = sorted(pathlib.Path(tmp).glob("chunk*.mp3"))
        return " ".join(_groq_transcribe(c, language) for c in chunks).strip()


def _groq_transcribe(path, language, tries=20):
    """POST one chunk to Groq, waiting out 429s rather than giving up fast.

    The free tier caps audio-seconds-per-HOUR (7200s) well below a single
    long live stream's total audio, so a burst of chunks right after a 3h
    broadcast ends will get rate-limited partway through - that is expected,
    not a failure. `retry-after` tells us how long Groq wants us to wait.
    """
    key = os.environ["GROQ_API_KEY"]
    for attempt in range(tries):
        with open(path, "rb") as f:
            r = requests.post(
                "https://api.groq.com/openai/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {key}"},
                data={"model": GROQ_MODEL, "language": language,
                      "response_format": "text"},
                files={"file": (path.name, f, "audio/mpeg")},
                timeout=120,
            )
        if r.status_code == 200:
            return r.text.strip()
        if r.status_code == 429 and attempt < tries - 1:
            wait = int(r.headers.get("retry-after", 60))
            print(f"  groq rate limited, waiting {wait}s ({attempt + 1}/{tries})",
                  file=sys.stderr)
            time.sleep(wait)
            continue
        r.raise_for_status()
    raise RuntimeError(f"Groq transcription failed for {path}: still rate-limited "
                        f"after {tries} attempts")


def push_transcript(queue_dir, video_id, title, link, published_at, text):
    """Write one transcript as a queue file and push it to the qultura repo.

    Filename is the video id: re-running on the same video overwrites its own
    file instead of creating a duplicate, and a file's mere existence in the
    queue is not otherwise checked (see each worker's own local archive).
    """
    import json

    out_dir = REPO / queue_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{video_id}.json"
    out_path.write_text(json.dumps({
        "title": title,
        "link": link,
        "published_at": published_at,
        "text": text,
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    _git("add", str(out_path))
    _git("commit", "-m", f"transcript: {title[:60]}")
    for attempt in range(5):
        _git("fetch", "origin", "main")
        _git("rebase", "origin/main")
        if _run("push").returncode == 0:
            return
        print(f"  push rejected, retrying ({attempt + 1}/5)", file=sys.stderr)
        time.sleep(5)
    raise RuntimeError(f"push failed after retries: {out_path}")


def _git(*args):
    subprocess.run(["git", "-C", str(REPO), *args], check=True)


def _run(*args):
    return subprocess.run(["git", "-C", str(REPO), *args])
