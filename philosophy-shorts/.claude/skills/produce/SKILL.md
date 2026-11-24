---
name: produce
description: 1분 철학 쇼츠 에피소드를 에이전트 파이프라인으로 제작한다. "/produce 3" 처럼 편수를 받거나 "/produce EP002 --from storyboard" 처럼 특정 에피소드의 특정 단계부터 재개한다. 체크포인트(대본 승인·영상 승인)에서 멈추며 "--auto"가 있으면 자동 통과한다.
---
# /produce — 오케스트레이터 플레이북

인수: `[N | EPxxx] [--from <stage>] [--auto]`
작업 디렉터리: `philosophy-shorts/`. 모든 명령은 거기서 실행한다.

## 0. 준비
- `N`이면 `python3 tools/new_episode.py --count N` 으로 에피소드를 만들고 출력된 ID 목록을 기억한다.
- `EPxxx`면 `python3 tools/stage.py EPxxx status` 로 현재 단계를 읽고 `--from` 또는 첫 미완료 단계부터 시작한다.
- 에피소드가 여럿이면 **같은 단계는 병렬로** (한 응답에 여러 Agent 호출), 단계 간은 순차로 진행한다.

## 1. 리서치 → 2. 대본 → 3. 검수 (에피소드별 루프)
1. Agent `researcher` 에 "EPxxx 리서치" 요청.
2. Agent `writer` 에 "EPxxx 대본 작성" 요청.
3. Agent `reviewer` 에 "EPxxx 검수" 요청. `review.json` 의 verdict 를 읽는다.
   - `revise` 이면 Agent `writer` 에 "EPxxx 재작성 (review.json issues 반영)" → 다시 `reviewer`. **최대 2회**. 3번째도 revise면 `python3 tools/stage.py EPxxx review done verdict=hold` 후 그 에피소드는 보류하고 사용자에게 보고한다.
   - `pass` 이면 다음으로.

## 체크포인트 A (대본 승인)
- `--auto` 없으면 여기서 **멈춘다**: 사용자에게 에피소드별 script.md 경로, 제목 후보, 검수 점수를 표로 보고하고 턴을 끝낸다. 사용자가 승인하면 `python3 tools/stage.py EPxxx human_a done by=user` 후 `/produce EPxxx --from storyboard` 로 재개.
- `--auto` 면 `python3 tools/stage.py EPxxx human_a done by=auto` 하고 계속.

## 4. 스토리보드 → 5. 자산 → 6. 렌더
4. Agent `visual-director` 에 "EPxxx 스토리보드" 요청.
5. 자산 (오케스트레이터가 직접 실행):
   - 이미지: 세션에 이미지 생성 MCP 도구(예: HF Spaces Z-Image-Turbo, 9:16)가 있으면 storyboard.json 의 각 prompt 로 생성해 `assets/cut_NN.png` 로 저장한다. 없으면 `python3 tools/gen_images.py EPxxx` (HF_TOKEN 있으면 API, 없으면 placeholder).
   - 음성: `python3 tools/gen_tts.py EPxxx`. 실패(네트워크 차단 등)하면 무음으로 진행하되 보고에 반드시 적는다.
   - 자막: `python3 tools/build_subtitles.py EPxxx`
   - `python3 tools/stage.py EPxxx assets done`
6. `python3 tools/render.py EPxxx` → `final.mp4`. 성공 시 `python3 tools/stage.py EPxxx render done artifact=final.mp4`.
   - 확인용으로 `ffmpeg -ss 1 -i episodes/EPxxx/final.mp4 -frames:v 1 episodes/EPxxx/assets/frame_check.png` 를 뽑아 Read 로 자막·레이아웃을 눈으로 확인한다.

## 체크포인트 B (영상 승인)
- `--auto` 없으면 멈추고 final.mp4 경로를 보고한다. 승인 시 `stage.py EPxxx human_b done by=user` → `/produce EPxxx --from publish`.
- `--auto` 면 `stage.py EPxxx human_b done by=auto`.

## 7. 퍼블리시
- Agent `publisher` 에 "EPxxx 메타데이터" 요청. 실제 업로드(`tools/publish.py EPxxx --upload`)는 **항상 사람이** 실행한다. 오케스트레이터는 절대 `--upload` 를 쓰지 않는다.

## 보고
끝나면 에피소드별로 한 줄: ID, 철학자/개념, 검수 점수, 산출물 경로, 빠진 것(예: TTS 무음). 커밋은 사용자가 요청했을 때만.
