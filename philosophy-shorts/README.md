# 1분 철학 — 에이전트 제작 파이프라인

기획: [PLAN.md](PLAN.md)

## 빠른 시작 (Claude Code)
```
cd philosophy-shorts
/produce 3           # 주제 뱅크에서 3편 → 대본 승인 체크포인트까지
/produce 3 --auto    # 체크포인트 자동 통과, final.mp4 와 metadata.json 까지
/produce EP002 --from storyboard
```

## 구성
| 경로 | 내용 |
|---|---|
| `.claude/agents/` | researcher · writer · reviewer · visual-director · publisher · analyst 서브에이전트 |
| `.claude/skills/produce/` | 오케스트레이터 플레이북 (`/produce`) |
| `prompts/` | 각 에이전트의 역할 프롬프트 (단일 출처, 에이전트가 시작 시 읽음) |
| `style/` | 화풍 접두어, 자막 규격, 보이스 설정 |
| `topics/bank.yaml` | 주제 뱅크 30개 (weight·status) |
| `tools/` | 상태 갱신, 대본 검증, 자막, TTS, 이미지, ffmpeg 렌더, 업로드 |
| `episodes/EPxxx/` | brief.md → script.md → review.json → storyboard.json → assets/ → final.mp4 → metadata.json |

## 환경변수 (선택)
- `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID` — 없으면 edge-tts 사용
- `HF_TOKEN` — 없으면 placeholder 이미지 (또는 세션의 이미지 MCP 도구 사용)
- `BGM_FILE` — 라이선스 음원 경로
- `YT_CLIENT_SECRETS` — 업로드용 OAuth 클라이언트 (업로드는 사람이 `tools/publish.py EPxxx --upload`)

## 사람이 하는 일 (주 40분)
1. 체크포인트 A: `script.md` 읽고 승인 → `python3 tools/stage.py EPxxx human_a done by=user`
2. 체크포인트 B: `final.mp4` 보고 승인 → `python3 tools/stage.py EPxxx human_b done by=user`
3. 업로드: `python3 tools/publish.py EPxxx --upload`
