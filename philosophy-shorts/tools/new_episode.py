#!/usr/bin/env python3
"""주제 뱅크에서 다음 주제를 꺼내 에피소드 폴더를 만든다.
사용: python3 tools/new_episode.py            # weight 최고 queued 주제 1개
      python3 tools/new_episode.py --topic T03
      python3 tools/new_episode.py --count 3
"""
import argparse, json
from datetime import datetime, timezone, timedelta
import yaml
from common import ROOT, EPISODES, STAGES, die

BANK = ROOT / "topics" / "bank.yaml"

def next_id() -> str:
    EPISODES.mkdir(exist_ok=True)
    nums = [int(p.name[2:]) for p in EPISODES.iterdir() if p.is_dir() and p.name.startswith("EP") and p.name[2:].isdigit()]
    return f"EP{(max(nums) + 1 if nums else 1):03d}"

def create(topic: dict) -> str:
    ep = next_id()
    d = EPISODES / ep
    d.mkdir()
    (d / "assets").mkdir()
    data = {
        "id": ep,
        "topic_id": topic["id"],
        "topic": {k: topic[k] for k in ("philosopher", "concept", "hook_situation", "source_hint")},
        "status": "new",
        "created_at": datetime.now(timezone(timedelta(hours=9))).isoformat(timespec="seconds"),
        "slot": None,
        "stages": {s: {"done": False} for s in STAGES},
    }
    (d / "episode.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return ep

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic")
    ap.add_argument("--count", type=int, default=1)
    a = ap.parse_args()
    bank = yaml.safe_load(BANK.read_text(encoding="utf-8"))
    topics = bank["topics"]
    picked = []
    if a.topic:
        t = next((t for t in topics if t["id"] == a.topic), None) or die(f"no topic {a.topic}")
        picked = [t]
    else:
        queued = sorted((t for t in topics if t["status"] == "queued"), key=lambda t: (-t["weight"], t["id"]))
        picked = queued[: a.count]
    if not picked:
        die("no queued topics")
    for t in picked:
        ep = create(t)
        t["status"] = "in_progress"
        t["episode"] = ep
        print(f"{ep}\t{t['id']}\t{t['philosopher']} — {t['concept']}")
    BANK.write_text(yaml.safe_dump(bank, allow_unicode=True, sort_keys=False), encoding="utf-8")

if __name__ == "__main__":
    main()
