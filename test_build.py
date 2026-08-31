"""Offline checks for the pure logic in build.py. Run: python test_build.py"""

from datetime import datetime, timedelta, timezone

from build import fresh, is_dupe, score

now = datetime.now(timezone.utc)
old = {"seen_at": (now - timedelta(days=30)).isoformat(), "title": "old"}
new = {"seen_at": now.isoformat(), "title": "Gemini gets a new reasoning mode"}

assert fresh([old, new]) == [new]
assert is_dupe("Gemini gets a new reasoning mode!", [new])
assert not is_dupe("Roma beat Lazio in the derby", [new])
assert score({"relevance": 4}, 3) == 12
print("ok")
