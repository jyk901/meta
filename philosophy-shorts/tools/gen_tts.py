#!/usr/bin/env python3
"""내레이션 음성 생성 → assets/narration.mp3
우선순위: ELEVENLABS_API_KEY 있으면 ElevenLabs, 없으면 edge-tts.
사용: python3 tools/gen_tts.py EP001 [--voice ko-KR-InJoonNeural]
"""
import argparse, asyncio, json, os, subprocess, sys
from common import ep_dir, parse_script, die

PAUSE = {1: 0.6}  # 구간 n 뒤 쉼(초). 기본 0.4

def narration_text(secs) -> str:
    out = []
    for sec in secs:
        out.append(sec["text"].strip())
    return "\n\n".join(out)

def elevenlabs(text: str, out) -> None:
    import urllib.request
    key = os.environ["ELEVENLABS_API_KEY"]
    voice = os.environ.get("ELEVENLABS_VOICE_ID") or die("ELEVENLABS_VOICE_ID 필요")
    body = json.dumps({"text": text, "model_id": "eleven_multilingual_v2",
                       "voice_settings": {"stability": 0.5, "similarity_boost": 0.75, "speed": 1.05}}).encode()
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{voice}", data=body,
                                 headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"})
    with urllib.request.urlopen(req, timeout=120) as r:
        out.write_bytes(r.read())

def edge(text: str, out, voice: str) -> None:
    import edge_tts
    async def run():
        c = edge_tts.Communicate(text, voice, rate="+5%", proxy=os.environ.get("HTTPS_PROXY"))
        await c.save(str(out))
    asyncio.run(run())

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("ep"); ap.add_argument("--voice", default="ko-KR-InJoonNeural")
    a = ap.parse_args()
    d = ep_dir(a.ep); secs = parse_script(d / "script.md")["sections"]
    text = narration_text(secs)
    out = d / "assets" / "narration.mp3"
    if os.environ.get("ELEVENLABS_API_KEY"):
        elevenlabs(text, out); engine = "elevenlabs"
    else:
        edge(text, out, a.voice); engine = f"edge-tts:{a.voice}"
    if not out.exists() or out.stat().st_size == 0:
        die("TTS 실패: 출력 파일이 비어 있음")
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out)], capture_output=True, text=True).stdout.strip())
    (d / "assets" / "narration.json").write_text(json.dumps({"engine": engine, "duration": dur, "chars": len(text)}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{a.ep}: {engine} {dur:.1f}s")
    if dur > 59.5:
        print("경고: 59.5초 초과 — 대본을 줄이거나 속도를 올리세요", file=sys.stderr)

if __name__ == "__main__":
    main()
