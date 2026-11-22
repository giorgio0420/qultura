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
MAX_CHARS = 150000  # ~40k tokens: a 2h video fits whole; median transcript is ~10k chars

LANGS = {"en": "English", "it": "Italian"}

# What each category is actually about. A source can publish outside its lane -
# a football magazine running a piece on a Guitar Hero record - and a well-written
# off-topic article would otherwise score high on craft alone.
SCOPE = {
    "ai": "artificial intelligence, robotics, electronics, embedded and control systems, "
          "semiconductors, space engineering, software engineering",
    "calcio": "football: tactics, match and squad analysis, AS Roma, Serie A, transfers, coaching",
    "musica": "music: criticism, analysis of records and scenes, artists and their work. "
              "Release dates, tracklists, tour and chart announcements are not analysis: "
              "skip them even when the artist is one the reader follows",
    "scacchi": "chess: openings, games, players, tournaments",
    "running": "running, endurance training, calisthenics, sports physiology",
    "filosofia": "philosophy, culture, cinema, essays and ideas",
    "mondo": "geopolitics, economics and current affairs explained with data, "
             "history and mechanism - not commentary or outrage",
}

SYSTEM = """You are the editor of a personal daily paper, and a writer, not a summarizer.
Work only from the text given. Never invent facts, quotes or connections the text does not make.
Drop intros, sponsor reads, calls to subscribe and generic filler. Never drop the author:
the voice, the angle, the odd example and the turn of phrase are the substance.
The reader is an engineer who also loves culture, music, football and ideas. He prefers
an original opinion, a strange angle or a well-made sentence to a neutral recap, and he can
only read a few pieces a day, so each one has to be worth it.
If the text is pure marketing, a bare announcement or too thin to read, set skip=true
and leave the other fields empty.

Write title, subtitle and summary in {lang}, whatever language the source is in.
When you translate, translate the voice too: keep its register, rhythm and irony.

Rate relevance on this scale, and use its whole range - most pieces are a 3:
5 - rare: original thinking or reporting, a voice of its own, you will not find it elsewhere
4 - strong: real substance or a distinct angle, worth the reading time
3 - ordinary: competent but routine, the usual daily article
2 - thin: mostly recap, quotes or context you already know
1 - vacuous: nothing an informed reader would learn
Originality and form count: a well-argued unconventional opinion is a 4 or 5, never chatter.
Generic opinion, gossip and rehashed takes are a 2."""

WRITE_NOTE = """
How to write summary: it is a short piece of the paper, in continuous prose, never a list.
Weigh each point by how much it matters and let the sentences follow one another with real
logic (this happened, which led to that, which matters because...). Carry the author's
register: if they are ironic, be dry; if they are lyrical, keep the images; if they are
blunt, be blunt. Keep the author's best image, example or sentence, quoted verbatim
(translated if needed) in quotation marks when it is short and exact; invent nothing.
Open on the fact or the claim, never on "The text", "The author" or "The article".
Never use bullet points, numbered lists, labels like "Key points", or closing morals.
Do not pad - say what matters and stop."""

# How to write the summary of a spoken piece, by kind of video (sources.json "format").
FORMATS = {
    "lezione": "The video teaches something. Say what it explains, then the mechanism or "
               "argument step by step with the concrete names, numbers and examples it uses, "
               "then the one thing worth remembering.",
    "opinione": "The video is one person's argument. State the thesis, then the supporting "
                "arguments in the order made, with the speaker's own examples. Say plainly "
                "where it is only assertion or opinion rather than shown.",
    "calcio": "Football talk. Lead with tactics, numbers and concrete match facts, name "
              "players and games, and keep verdicts apart from facts. No banter.",
    "intervista": "An interview or press conference. Say who speaks, then the 3-5 concrete "
                  "facts or claims, attributed. Drop pleasantries and stock phrases.",
}


class QuotaExceeded(RuntimeError):
    """The daily free-tier allowance for this model is gone; retrying will not help."""


SCHEMA = {
    "type": "object",
    "properties": {
        "skip": {"type": "boolean"},
        "title": {"type": "string"},
        "subtitle": {"type": "string"},
        "summary": {"type": "string"},
        "relevance": {"type": "integer"},
    },
    "required": ["skip", "title", "subtitle", "summary", "relevance"],
}


def curate(title, text, category, lang="en", focus=None, prose=False, keep_all=False,
           format=None):
    """Return the curated record for one piece of content.

    prose: True for YouTube-sourced (spoken) content - adds the per-format shape.
    format: key of FORMATS, how to structure the summary of a spoken piece.
    keep_all: this source is never out of scope - skip must stay false, even
    when the episode only briefly touches what the reader actually follows.
    """
    name = LANGS.get(lang, lang)
    scope = SCOPE.get(category, category)
    care = ("The reader follows these closely: " + focus + "." + chr(10)) if focus else ""
    scope_instr = (
        "This source is always in scope for this category - never set skip=true, "
        "whatever the episode covers. Still write a real title and summary of what "
        "was actually said, even when it barely touches what the reader follows."
        if keep_all else
        f"This category covers: {scope}.\n"
        "If the piece falls outside that scope, set skip=true - however well written it is."
    )
    # ~1 summary word per 60 transcript chars: 10k chars -> 170 words, capped at 450
    words = max(120, min(450, len(text) // 40))
    shape = (FORMATS.get(format, "") + " " if prose else "") +         f"Aim for about {words} words of summary."
    prompt = f"""Category: {category}
Original title: {title}

Content:
{text[:MAX_CHARS]}

{scope_instr}
{care}Write a subtitle of at most 100 characters: one line in the author's own register
that makes the piece worth opening, concrete, no clickbait.
{shape}
Rate relevance 1-5 on the anchored scale; a piece about someone the reader follows
is worth one point more, but an announcement with no substance stays low.
Write in {name}: the title, the subtitle and the summary must be in {name},
translated if the source is in another language."""
    system = SYSTEM.format(lang=LANGS.get(lang, lang)) + WRITE_NOTE
    body = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": SCHEMA,
            "temperature": 0.6,
        },
    }
    raw = _post(body)
    if not raw.get("candidates"):
        # blocked prompt or empty answer: say why instead of a bare KeyError
        raise RuntimeError("Gemini returned no candidates: "
                           + json.dumps(raw.get("promptFeedback", raw))[:300])
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
