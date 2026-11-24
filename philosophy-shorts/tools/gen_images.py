#!/usr/bin/env python3
"""storyboard.json → assets/cut_NN.png
모드:
  --mode hf           Hugging Face Inference API (HF_TOKEN 필요, FLUX.1-schnell)
  --mode placeholder  Pillow로 스타일 가이드 색상의 카드 생성 (API 없이 포맷 검증용)
  (기본: HF_TOKEN 있으면 hf, 없으면 placeholder)
Claude Code 세션에서는 MCP 이미지 도구(예: HF Spaces Z-Image-Turbo)로 직접 생성한 PNG를
assets/cut_NN.png 이름으로 저장해도 된다. 이 스크립트는 빠진 컷만 채운다 (--force 로 전부 재생성).
"""
import argparse, json, os, sys, time
from pathlib import Path
from common import ep_dir, ROOT, die

W, H = 1080, 1920
BG, FG, AMBER = (18, 18, 20), (244, 241, 234), (242, 177, 52)

def placeholder(cut: dict, out: Path) -> None:
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGB", (W, H), BG)
    dr = ImageDraw.Draw(img)
    # 앰버 광원 느낌의 원
    cx, cy, r = W // 2, int(H * 0.42), 260
    for i in range(r, 0, -4):
        a = int(60 * (1 - i / r))
        dr.ellipse([cx - i, cy - i, cx + i, cy + i], fill=(BG[0] + a, BG[1] + a // 2, BG[2]))
    try:
        font = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 54)
        small = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 34)
    except OSError:
        font = small = ImageFont.load_default()
    dr.text((cx, int(H * 0.72)), f"CUT {cut['n']:02d}  ·  {cut['start']}–{cut['end']}s", fill=AMBER, font=font, anchor="mm")
    dr.text((cx, int(H * 0.78)), cut["prompt"][:60].rsplit(",", 1)[0][-60:], fill=FG, font=small, anchor="mm")
    img.save(out)

def hf(cut: dict, out: Path) -> None:
    import urllib.request
    token = os.environ["HF_TOKEN"]
    model = os.environ.get("HF_IMAGE_MODEL", "black-forest-labs/FLUX.1-schnell")
    body = json.dumps({"inputs": cut["prompt"], "parameters": {"width": 768, "height": 1344, "num_inference_steps": 4}}).encode()
    req = urllib.request.Request(f"https://router.huggingface.co/hf-inference/models/{model}", data=body,
                                 headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                out.write_bytes(r.read()); return
        except Exception as e:  # 모델 로딩 503 등
            if attempt == 2: raise
            print(f"  retry {attempt+1}: {e}", file=sys.stderr); time.sleep(15)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("ep"); ap.add_argument("--mode", choices=["hf", "placeholder"]); ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    mode = a.mode or ("hf" if os.environ.get("HF_TOKEN") else "placeholder")
    d = ep_dir(a.ep); sb = json.loads((d / "storyboard.json").read_text(encoding="utf-8"))
    made = 0
    for cut in sb["cuts"]:
        out = d / "assets" / f"cut_{cut['n']:02d}.png"
        if out.exists() and not a.force:
            continue
        (hf if mode == "hf" else placeholder)(cut, out); made += 1
        print(f"  cut {cut['n']:02d} ← {mode}")
    print(f"{a.ep}: {made} generated, {len(sb['cuts'])} total ({mode})")

if __name__ == "__main__":
    main()
