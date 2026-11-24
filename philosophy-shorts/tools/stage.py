#!/usr/bin/env python3
"""episode.json 단계 갱신.
사용: python3 tools/stage.py EP001 review done artifact=review.json verdict=pass
      python3 tools/stage.py EP001 script done artifact=script.md revisions=+1
      python3 tools/stage.py EP001 status   (현재 상태 출력)
"""
import sys
from datetime import datetime, timezone, timedelta
from common import load_episode, save_episode, STAGES, die

KST = timezone(timedelta(hours=9))

def main():
    if len(sys.argv) < 2:
        die(__doc__)
    ep = sys.argv[1]
    data = load_episode(ep)
    if len(sys.argv) == 2 or sys.argv[2] == "status":
        done = [s for s in STAGES if data["stages"].get(s, {}).get("done")]
        print(f"{ep} status={data['status']} done={done}")
        return
    stage, flag = sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "done"
    if stage not in STAGES:
        die(f"unknown stage {stage}; one of {STAGES}")
    st = data["stages"].setdefault(stage, {})
    st["done"] = flag == "done"
    st["at"] = datetime.now(KST).isoformat(timespec="seconds")
    for kv in sys.argv[4:]:
        k, v = kv.split("=", 1)
        if v.startswith("+"):
            st[k] = int(st.get(k, 0)) + int(v[1:])
        else:
            st[k] = v
    # 상태 문자열: 마지막으로 끝난 단계
    if st["done"]:
        nxt = {"research": "researched", "script": "scripted", "review": "reviewed", "human_a": "script_approved",
               "storyboard": "storyboarded", "assets": "assets_ready", "render": "rendered",
               "human_b": "video_approved", "publish": "published", "analytics": "analyzed"}[stage]
        if stage == "review" and st.get("verdict") == "revise":
            nxt = "needs_revision"
        data["status"] = nxt
    save_episode(ep, data)
    print(f"{ep} {stage} -> {st}")

if __name__ == "__main__":
    main()
