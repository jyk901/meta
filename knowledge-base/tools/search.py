#!/usr/bin/env python3
"""위키 키워드 검색. 사용법: python3 tools/search.py 검색어 [검색어 ...]
모든 검색어가 들어간 페이지를 일치 횟수 순으로 보여준다."""
import pathlib, sys

wiki = pathlib.Path(__file__).resolve().parent.parent / "wiki"
terms = [t.lower() for t in sys.argv[1:]]
if not terms:
    sys.exit(__doc__)
hits = []
for p in wiki.rglob("*.md"):
    text = p.read_text(encoding="utf-8", errors="ignore")
    low = text.lower()
    if all(t in low for t in terms):
        score = sum(low.count(t) for t in terms)
        line = next((l.strip() for l in text.splitlines() if any(t in l.lower() for t in terms)), "")
        hits.append((score, p.relative_to(wiki), line))
for score, path, line in sorted(hits, reverse=True):
    print(f"{score:4d}  {path}\n      {line[:120]}")
if not hits:
    print("결과 없음")
