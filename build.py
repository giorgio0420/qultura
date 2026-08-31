"""Step 3: run the whole daily pipeline and write data.json for the PWA.

    GEMINI_API_KEY=... python build.py
"""

import difflib
import json
import os
import pathlib
import sys
import time
import traceback
from datetime import datetime, timedelta, timezone

def load_env(path=".env"):
    """Read KEY=value lines from .env so a local run needs no exported variable.

    PowerShell's `>` writes UTF-16, so sniff the encoding rather than assuming UTF-8.
    CI has no .env and passes a real environment variable instead.
    """
    if not pathlib.Path(path).exists():
        return
    raw = pathlib.Path(path).read_bytes()
    enc = "utf-16" if 0 in raw[:4] else "utf-8-sig"  # null bytes mean UTF-16
    for line in raw.decode(enc).splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip("\"'"))


load_env()

from curate import QuotaExceeded, curate
from ingest import SOURCES, fetch

OUT = "data.json"
KEEP_DAYS = 14
PAUSE = 4  # seconds between LLM calls: the free tier allows ~10 requests/minute
MIN_RELEVANCE = 3


def load(path=OUT):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)["items"]
    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        return []


def fresh(items, days=KEEP_DAYS):
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    return [i for i in items if i["seen_at"] >= cutoff]


def is_dupe(title, items, threshold=0.82):
    """True if a kept item already says roughly the same thing.

    ponytail: title-only similarity. Swap in sentence-transformer embeddings over
    the summaries if near-duplicates from different sources start slipping through.
    """
    return any(difflib.SequenceMatcher(None, title.lower(), i["title"].lower()).ratio()
               >= threshold for i in items)


def score(item, weight):
    return weight * item["relevance"]


def run():
    items = fresh(load())
    seen = {i["link"] for i in items}
    added = 0

    for src in SOURCES:
        print(f"\n=== {src['name']} ===", flush=True)
        try:
            contents = list(fetch(src, seen))
        except Exception:
            traceback.print_exc(limit=1)
            continue

        for title, link, text in contents:
            if not text.strip():
                continue
            seen.add(link)
            try:
                c = curate(title, text, src["category"], src.get("out_lang", "en"),
                           src.get("focus"))
            except QuotaExceeded as e:
                # Out of daily allowance: every further call fails the same way, so
                # stop and keep what we have instead of grinding through the backoff.
                print("quota exhausted, stopping early: " + str(e)[:200], flush=True)
                return save(items, added)
            except Exception:
                traceback.print_exc(limit=1)
                continue
            time.sleep(PAUSE)

            if c["skip"] or c["relevance"] < MIN_RELEVANCE:
                print(f"  [drop] {title}", flush=True)
                continue
            if is_dupe(c["title"], items):
                print(f"  [dupe] {title}", flush=True)
                continue

            items.append({
                "title": c["title"],
                "original_title": title,
                "link": link,
                "source": src["name"],
                "category": src["category"],
                "kind": src["kind"],
                "lang": src.get("out_lang", "en"),
                "summary": c["summary"],
                "bullets": c["bullets"],
                "relevance": c["relevance"],
                "score": score(c, src["weight"]),
                "seen_at": datetime.now(timezone.utc).isoformat(),
            })
            added += 1
            print(f"  [keep] {c['relevance']}/5 {c['title']}", flush=True)

    items.sort(key=lambda i: (i["seen_at"][:10], i["score"]), reverse=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"generated_at": datetime.now(timezone.utc).isoformat(),
                   "items": items}, f, ensure_ascii=False, indent=1)
    print(f"\n{added} new, {len(items)} total -> {OUT}")
    return added


if __name__ == "__main__":
    if not os.environ.get("GEMINI_API_KEY"):
        sys.exit("GEMINI_API_KEY not set")
    run()
