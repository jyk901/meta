#!/usr/bin/env python3
"""metadata.json 검증(--dry-run, 기본) 및 YouTube 업로드(--upload).
업로드에는 google-api-python-client + OAuth client_secrets.json (환경변수 YT_CLIENT_SECRETS) 이 필요하다.
"""
import argparse, json, sys
from common import ep_dir, die

REQ = ["title", "description", "tags", "hashtags", "pinned_comment", "thumbnail_text", "altered_content", "category_id"]

def validate(m: dict) -> list:
    e = []
    for k in REQ:
        if k not in m: e.append(f"누락: {k}")
    if len(m.get("title", "")) > 40: e.append("제목 40자 초과")
    if "!" in m.get("title", ""): e.append("제목에 느낌표")
    if "#Shorts" in m.get("title", ""): e.append("제목에 #Shorts 금지")
    if "AI" not in m.get("description", ""): e.append("설명에 AI 생성 고지 없음")
    for h in ("#1분철학", "#철학", "#Shorts"):
        if h not in m.get("hashtags", []): e.append(f"해시태그 누락: {h}")
    if not (5 <= len(m.get("hashtags", [])) <= 8): e.append("해시태그 5~8개")
    if len(m.get("thumbnail_text", "")) > 14: e.append("썸네일 문구 14자 초과")
    if m.get("altered_content") is not True: e.append("altered_content 는 true")
    return e

def upload(ep, m):
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        die("pip install google-api-python-client google-auth-oauthlib")
    import os
    flow = InstalledAppFlow.from_client_secrets_file(os.environ["YT_CLIENT_SECRETS"], ["https://www.googleapis.com/auth/youtube.upload"])
    creds = flow.run_local_server(port=0)
    yt = build("youtube", "v3", credentials=creds)
    body = {"snippet": {"title": m["title"], "description": m["description"] + "\n" + " ".join(m["hashtags"]),
                        "tags": m["tags"], "categoryId": m["category_id"], "defaultLanguage": "ko"},
            "status": {"privacyStatus": "private" if m.get("publish_at") else "public", "selfDeclaredMadeForKids": False,
                       **({"publishAt": m["publish_at"]} if m.get("publish_at") else {}),
                       "containsSyntheticMedia": True}}
    media = MediaFileUpload(str(ep_dir(ep) / "final.mp4"), chunksize=-1, resumable=True)
    res = yt.videos().insert(part="snippet,status", body=body, media_body=media).execute()
    print("uploaded:", res["id"])

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("ep"); ap.add_argument("--upload", action="store_true"); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    m = json.loads((ep_dir(a.ep) / "metadata.json").read_text(encoding="utf-8"))
    errs = validate(m)
    if errs:
        print(json.dumps({"ok": False, "errors": errs}, ensure_ascii=False, indent=2)); sys.exit(1)
    print(json.dumps({"ok": True, "title": m["title"]}, ensure_ascii=False))
    if a.upload:
        if not (ep_dir(a.ep) / "final.mp4").exists(): die("final.mp4 없음")
        upload(a.ep, m)

if __name__ == "__main__":
    main()
