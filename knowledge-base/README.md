# 개인 LLM 지식 베이스 (Karpathy "LLM Wiki" 방식)

## 사용법
1. 이 폴더에서 Claude Code 실행: `cd knowledge-base && claude` (CLAUDE.md 규칙이 자동 적용됨)
2. 기사·논문·메모를 `raw/`에 넣기 (웹 기사는 Obsidian Web Clipper로 마크다운 저장 추천)
3. Claude에게 말하기:
   - `raw/파일명.md 를 ingest 해줘`
   - `○○에 대해 위키 기반으로 정리해줘`
   - `위키 점검(lint) 해줘`
4. (선택) 이 폴더를 Obsidian 보관소로 열면 그래프 뷰로 위키를 둘러볼 수 있음.
   설정 → 파일 및 링크 → 첨부파일 폴더를 `raw/assets`로 지정.

검색: `python3 tools/search.py 검색어`
