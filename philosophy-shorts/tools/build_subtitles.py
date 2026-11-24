#!/usr/bin/env python3
"""script.md + 내레이션 길이 → assets/subs.ass (렌더용), assets/subs.srt (유튜브 자막 업로드용), assets/cues.json
문장별 시간은 구간 계획 시간을 실제 오디오 길이에 맞춰 비례 배분한다.
storyboard.json 이 있으면 각 컷의 caption_emphasis 단어를 앰버색으로 강조한다.
사용: python3 tools/build_subtitles.py EP001 [--duration 57.2]
"""
import argparse, json, re, subprocess
from common import ep_dir, parse_script, split_sentences

MAX_LINE = 14
W, H = 1080, 1920
AMBER_ASS = "&H0034B1F2&"   # #F2B134 → BGR

def wrap(text: str, br: str) -> str:
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) > MAX_LINE and cur:
            lines.append(cur); cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur: lines.append(cur)
    if len(lines) > 2:
        lines = [" ".join(lines[:-1]), lines[-1]]
    return br.join(lines)

def ts_srt(sec: float) -> str:
    ms = int(round(sec * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def ts_ass(sec: float) -> str:
    cs = int(round(sec * 100)); h, cs = divmod(cs, 360000); m, cs = divmod(cs, 6000); s, cs = divmod(cs, 100)
    return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"

def audio_duration(path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return float(out.stdout.strip())

def emphasize(text: str, words) -> str:
    for w in sorted(set(words), key=len, reverse=True):
        if w and w in text:
            text = text.replace(w, "{\\c" + AMBER_ASS + "}" + w + "{\\c&H00EAF1F4&}")
    return text

ASS_HEADER = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Body,Noto Sans CJK KR,{int(W*0.058)},&H00EAF1F4,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,0,2,60,60,{int(H*0.28)},1
Style: Hook,Noto Sans CJK KR,{int(W*0.058)},&H00EAF1F4,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,0,2,60,60,{int(H*0.20)},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("ep"); ap.add_argument("--duration", type=float)
    a = ap.parse_args()
    d = ep_dir(a.ep); s = parse_script(d / "script.md"); secs = s["sections"]
    planned_end = secs[-1]["end"]
    dur = a.duration
    if dur is None:
        nar = d / "assets" / "narration.mp3"
        dur = audio_duration(nar) if nar.exists() else float(planned_end)
    scale = dur / planned_end
    sb_path = d / "storyboard.json"
    cuts = json.loads(sb_path.read_text(encoding="utf-8"))["cuts"] if sb_path.exists() else []
    cues = []
    for sec in secs:
        sents = split_sentences(sec["text"])
        total = sum(len(re.sub(r"\s", "", x)) for x in sents) or 1
        t0, t1 = sec["start"] * scale, sec["end"] * scale
        t = t0
        for x in sents:
            w = len(re.sub(r"\s", "", x)) / total * (t1 - t0)
            cues.append({"section": sec["n"], "start": round(t, 3), "end": round(min(t + w, t1) - 0.05, 3), "text": x})
            t += w
    srt = "\n".join(f"{i}\n{ts_srt(c['start'])} --> {ts_srt(c['end'])}\n{wrap(c['text'], chr(10))}\n" for i, c in enumerate(cues, 1))
    (d / "assets" / "subs.srt").write_text(srt, encoding="utf-8")
    lines = [ASS_HEADER]
    for c in cues:
        cut = next((k for k in cuts if k["start"] * scale <= c["start"] < k["end"] * scale), None)
        emph = cut.get("caption_emphasis", []) if cut else []
        style = "Hook" if c["section"] == 1 else "Body"
        txt = emphasize(wrap(c["text"], "\\N"), emph)
        lines.append(f"Dialogue: 0,{ts_ass(c['start'])},{ts_ass(c['end'])},{style},,0,0,0,,{txt}")
    (d / "assets" / "subs.ass").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (d / "assets" / "cues.json").write_text(json.dumps({"duration": dur, "scale": scale, "cues": cues}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{a.ep}: {len(cues)} cues, duration={dur:.1f}s scale={scale:.3f}, emphasis from {'storyboard' if cuts else 'none'}")

if __name__ == "__main__":
    main()
