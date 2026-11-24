"""공용 유틸: 경로, episode.json, script.md 파서."""
import json, re, sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
EPISODES = ROOT / "episodes"
STAGES = ["research", "script", "review", "human_a", "storyboard", "assets", "render", "human_b", "publish", "analytics"]
SECTION_NAMES = ["훅", "문제", "사상", "적용", "마무리"]

def ep_dir(ep: str) -> Path:
    return EPISODES / ep

def load_episode(ep: str) -> dict:
    return json.loads((ep_dir(ep) / "episode.json").read_text(encoding="utf-8"))

def save_episode(ep: str, data: dict) -> None:
    (ep_dir(ep) / "episode.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

_HDR = re.compile(r"^##\s*(\d)\.\s*(\S+)\s*\((\d+)\s*-\s*(\d+)\)\s*$", re.M)

def parse_script(path: Path) -> dict:
    """script.md → {"meta": {...}, "sections": [{"n","name","start","end","text"}]}"""
    raw = path.read_text(encoding="utf-8")
    meta = {}
    body = raw
    if raw.startswith("---"):
        _, fm, body = raw.split("---", 2)
        meta = yaml.safe_load(fm) or {}
    heads = list(_HDR.finditer(body))
    sections = []
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(body)
        text = body[m.end():end].strip()
        sections.append({"n": int(m.group(1)), "name": m.group(2), "start": int(m.group(3)), "end": int(m.group(4)), "text": text})
    return {"meta": meta, "sections": sections}

def narration_chars(sections) -> int:
    return sum(len(re.sub(r"\s+", "", s["text"])) for s in sections)

def split_sentences(text: str):
    text = re.sub(r"\s+", " ", text).strip()
    parts = re.split(r"(?<=[.?!。])\s+", text)
    return [p for p in parts if p]

def die(msg: str, code: int = 1):
    print(msg, file=sys.stderr)
    sys.exit(code)
