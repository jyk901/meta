---
title: LLM Wiki
type: concept
sources: [https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f]
updated: 2026-11-28
---
# LLM Wiki

Andrej Karpathy가 제안한 개인 지식 베이스 패턴. 질문할 때마다 원문 조각을 다시 찾는 RAG 대신,
LLM이 원본 자료를 읽고 서로 링크된 마크다운 위키를 **점점 쌓아가며** 관리한다.

- 3층 구조: 원본(raw, 불변) → 위키(LLM 소유) → 스키마(CLAUDE.md, 규칙)
- 3가지 작업: ingest(자료 넣기), query(질문), lint(점검)
- `index.md`(내용 목록)와 `log.md`(시간순 기록)로 길찾기 — 자료 ~100개 규모까지는 임베딩 없이도 잘 동작
- 비유: "Obsidian은 IDE, LLM은 프로그래머, 위키는 코드베이스"
- 핵심 통찰: 지식 관리의 병목은 상호참조·요약·모순 정리 같은 '장부 정리'인데, 이는 LLM에게 거의 공짜다.
