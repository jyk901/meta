#!/usr/bin/env python3
"""storyboard + assets → final.mp4 (1080x1920, 30fps)
필요: assets/cut_NN.png, assets/subs.ass (build_subtitles.py). 선택: assets/narration.mp3, BGM_FILE 환경변수.
사용: python3 tools/render.py EP001 [--preview]  (--preview: 540x960, 빠른 확인용)
"""
import argparse, json, os, subprocess
from pathlib import Path
from common import ep_dir, die

FONT_DIR = "/usr/share/fonts/opentype/noto"

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("ep"); ap.add_argument("--preview", action="store_true")
    a = ap.parse_args()
    d = ep_dir(a.ep); assets = d / "assets"
    sb = json.loads((d / "storyboard.json").read_text(encoding="utf-8"))
    fps = sb.get("fps", 30)
    W, H = (540, 960) if a.preview else (1080, 1920)
    cuts = sb["cuts"]
    cues = json.loads((assets / "cues.json").read_text(encoding="utf-8")) if (assets / "cues.json").exists() else None
    scale = cues["scale"] if cues else 1.0
    total = cuts[-1]["end"] * scale

    inputs, fchain = [], []
    for i, c in enumerate(cuts):
        png = assets / f"cut_{c['n']:02d}.png"
        if not png.exists(): die(f"missing {png}")
        dur = (c["end"] - c["start"]) * scale
        inputs += ["-loop", "1", "-framerate", str(fps), "-t", f"{dur:.3f}", "-i", str(png)]
        frames = int(dur * fps)
        m = c.get("motion", "zoom_in")
        z = {"zoom_in": "1+0.12*on/{n}", "zoom_out": "1.12-0.12*on/{n}", "pan_left": "1.12", "pan_right": "1.12"}[m].format(n=frames)
        x = {"pan_left": "(iw-iw/zoom)*(1-on/{n})", "pan_right": "(iw-iw/zoom)*on/{n}"}.get(m, "(iw-iw/zoom)/2").format(n=frames)
        fchain.append(
            f"[{i}:v]scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},"
            f"zoompan=z='{z}':x='{x}':y='(ih-ih/zoom)/2':d=1:s={W}x{H}:fps={fps},"
            f"fade=t=in:st=0:d=0.3,fade=t=out:st={max(dur-0.3,0):.2f}:d=0.3,setsar=1[v{i}]")
    concat = "".join(f"[v{i}]" for i in range(len(cuts))) + f"concat=n={len(cuts)}:v=1:a=0[vc]"
    # 비네트 + 자막
    subs = assets / "subs.ass"
    if not subs.exists(): die("missing subs.ass — run tools/build_subtitles.py first")
    vf = f"[vc]vignette=PI/5[vv];[vv]ass='{subs}':fontsdir='{FONT_DIR}'[vout]"
    hook = cuts[0].get("hook_text")
    if hook:
        hook_esc = hook.replace("'", "’").replace(":", "\\:")
        vf = vf.replace("[vout]", "[vh];[vh]drawtext=fontfile='" + FONT_DIR + "/NotoSansCJK-Bold.ttc':text='" + hook_esc +
                        f"':fontcolor=0xF2B134:fontsize={int(W*0.085)}:x=(w-text_w)/2:y=(h-text_h)/2-{int(H*0.08)}:"
                        f"enable='between(t,0,{cuts[0]['end']*scale:.2f})':borderw=4:bordercolor=black[vout]")
    fc = ";".join(fchain + [concat, vf])

    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + inputs
    nar = assets / "narration.mp3"; bgm = os.environ.get("BGM_FILE")
    amaps = []
    ai = len(cuts)
    if nar.exists():
        cmd += ["-i", str(nar)]; amaps.append(f"[{ai}:a]volume=1.0[a0]"); ai += 1
    if bgm and Path(bgm).exists():
        cmd += ["-stream_loop", "-1", "-i", bgm]; amaps.append(f"[{ai}:a]volume=-22dB,afade=t=out:st={total-2:.2f}:d=2[a1]"); ai += 1
    if amaps:
        mix = ("".join(f"[a{k}]" for k in range(len(amaps))) + f"amix=inputs={len(amaps)}:duration=first:normalize=0[aout]") if len(amaps) > 1 else "[a0]anull[aout]"
        fc += ";" + ";".join(amaps) + ";" + mix
    else:
        cmd += ["-f", "lavfi", "-t", f"{total:.3f}", "-i", "anullsrc=r=44100:cl=stereo"]; fc += f";[{ai}:a]anull[aout]"
    out = d / ("preview.mp4" if a.preview else "final.mp4")
    cmd += ["-filter_complex", fc, "-map", "[vout]", "-map", "[aout]", "-t", f"{total:.3f}",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(fps),
            "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        die(r.stderr[-3000:])
    print(f"{a.ep}: {out.name} ({total:.1f}s, {W}x{H})")

if __name__ == "__main__":
    main()
