#!/usr/bin/env python3
"""script.md 형식·분량 검사. 통과 시 exit 0, JSON 출력."""
import json, re, sys
from pathlib import Path
from common import parse_script, narration_chars, SECTION_NAMES, split_sentences

MIN_CHARS, MAX_CHARS = 270, 320

def validate(path: Path) -> dict:
    errs, warns = [], []
    s = parse_script(path)
    meta, secs = s["meta"], s["sections"]
    for k in ("id", "philosopher", "concept", "source", "title_candidates"):
        if k not in meta:
            errs.append(f"frontmatter 누락: {k}")
    if len(meta.get("title_candidates") or []) < 3:
        errs.append("title_candidates 3개 필요")
    if [x["n"] for x in secs] != [1, 2, 3, 4, 5]:
        errs.append(f"구간 번호가 1~5가 아님: {[x['n'] for x in secs]}")
    for x, want in zip(secs, SECTION_NAMES):
        if x["name"] != want:
            errs.append(f"구간 {x['n']} 이름은 '{want}' 이어야 함 (현재 '{x['name']}')")
        if not x["text"]:
            errs.append(f"구간 {x['n']} 본문 없음")
    if secs:
        if secs[0]["start"] != 0:
            errs.append("1구간은 0초에서 시작")
        for a, b in zip(secs, secs[1:]):
            if a["end"] != b["start"]:
                errs.append(f"구간 {a['n']}→{b['n']} 시간이 이어지지 않음 ({a['end']}≠{b['start']})")
        if secs[-1]["end"] > 59:
            errs.append(f"마지막 구간 끝 {secs[-1]['end']}초 > 59")
    chars = narration_chars(secs)
    if not (MIN_CHARS <= chars <= MAX_CHARS):
        errs.append(f"공백 제외 글자 수 {chars} (허용 {MIN_CHARS}~{MAX_CHARS})")
    # 훅에 철학자 이름 금지
    phil = str(meta.get("philosopher", ""))
    tokens = [t for t in re.split(r"[\s·,]+", phil) if len(t) >= 2]
    if secs and any(t in secs[0]["text"] for t in tokens):
        errs.append("1구간(훅)에 철학자 이름이 있음")
    if len(secs) == 5:
        last = secs[4]["text"]
        if "?" not in last:
            errs.append("5구간에 질문(?)이 없음")
        if not last.rstrip().endswith("1분 철학이었습니다."):
            errs.append("5구간은 '1분 철학이었습니다.' 로 끝나야 함")
        if "댓글" not in last:
            warns.append("5구간에 댓글 유도가 없음")
        # 문장 길이 단조로움
        lens = [len(x) for sec in secs for x in split_sentences(sec["text"])]
        for i in range(len(lens) - 2):
            if max(lens[i:i+3]) - min(lens[i:i+3]) <= 3:
                warns.append("비슷한 길이 문장 3연속 (단조로움)")
                break
        if "!" in "".join(sec["text"] for sec in secs):
            warns.append("느낌표 사용 — 톤 가이드 위반 가능")
    return {"ok": not errs, "chars": chars, "errors": errs, "warnings": warns}

if __name__ == "__main__":
    r = validate(Path(sys.argv[1]))
    print(json.dumps(r, ensure_ascii=False, indent=2))
    sys.exit(0 if r["ok"] else 1)
