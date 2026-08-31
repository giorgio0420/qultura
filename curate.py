"""Step 2: turn raw text into a curated, structured record via the Gemini free tier.

Needs GEMINI_API_KEY (https://aistudio.google.com/apikey). No SDK: plain REST.
"""

import json
import os
import time
import urllib.error
import urllib.request

MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")
URL = ("https://generativelanguage.googleapis.com/v1beta/models/"
       f"{MODEL}:generateContent")
MAX_CHARS = 30000  # transcripts can be huge; free tier has token-per-minute limits

LANGS = {"en": "English", "it": "Italian"}

SYSTEM = """You are a ruthless editorial curator for a personal daily digest.
Work only from the text given. Never invent facts.
Strip intros, sponsor reads, calls to subscribe, and generic filler.
Keep only substance: technical content, tactical analysis, arguments, numbers, names.
If the text is pure marketing, an announcement with no analysis, or too thin to be
worth reading, set skip=true and leave the other fields empty.

Write title, summary and bullets in {lang}, whatever language the source is in.
Translate rather than quote: the reader wants to read {lang} and nothing else.

Rate relevance on this scale, and use its whole range - most pieces are a 3:
5 - rare: original reporting or analysis, dense with specifics you cannot get elsewhere
4 - strong: real substance, concrete detail, worth the reading time
3 - ordinary: competent but routine, the usual daily article
2 - thin: mostly recap, quotes or context you already know
1 - vacuous: nothing an informed reader would learn"""

class QuotaExceeded(RuntimeError):
    """The daily free-tier allowance for this model is gone; retrying will not help."""


SCHEMA = {
    "type": "object",
    "properties": {
        "skip": {"type": "boolean"},
        "title": {"type": "string"},
        "summary": {"type": "string"},
        "bullets": {"type": "array", "items": {"type": "string"}},
        "relevance": {"type": "integer"},
    },
    "required": ["skip", "title", "summary", "bullets", "relevance"],
}


def curate(title, text, category, lang="en"):
    """Return the curated record for one piece of content."""
    name = LANGS.get(lang, lang)
    prompt = f"""Category: {category}
Original title: {title}

Content:
{text[:MAX_CHARS]}

Summarize in 2-3 sentences, then 3-6 bullets of concrete substance.
Rate relevance 1-5 on the anchored scale.
Write in {name}: the title, the summary and every bullet must be in {name},
translated if the source is in another language."""
    body = {
        "systemInstruction": {"parts": [{"text": SYSTEM.format(lang=LANGS.get(lang, lang))}]},
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": SCHEMA,
            "temperature": 0.2,
        },
    }
    raw = _post(body)
    return json.loads(raw["candidates"][0]["content"]["parts"][0]["text"])


def _post(body, tries=4):
    """POST to Gemini, backing off on the free tier's rate limits."""
    key = os.environ["GEMINI_API_KEY"]
    req = urllib.request.Request(
        f"{URL}?key={key}", data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"})
    for attempt in range(tries):
        try:
            return json.loads(urllib.request.urlopen(req, timeout=120).read())
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 503) or attempt == tries - 1:
                detail = f"{e.code}: {e.read().decode()[:800]}"
                raise (QuotaExceeded if e.code == 429 else RuntimeError)(detail) from e
            time.sleep(5 * 2 ** attempt)


if __name__ == "__main__":
    from ingest import SOURCES, fetch

    src = SOURCES[0]
    title, link, text = next(iter(fetch(src)))
    print(f"{src['name']}: {title}\n{link}\nraw chars={len(text)}\n")
    print(json.dumps(curate(title, text, src["category"], src.get("out_lang", "en")),
                     indent=2, ensure_ascii=False))
