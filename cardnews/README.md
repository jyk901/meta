# 카드뉴스 메이커

주제를 입력하면 Claude가 10장짜리 인스타 카드뉴스(1080×1350)를 구성하고, 브라우저에서 바로 PNG로 저장할 수 있습니다.

```bash
cd cardnews
export ANTHROPIC_API_KEY=sk-ant-...   # 없으면 샘플 카드로 데모 동작
npm start                             # http://localhost:3000
```

- 카드 클릭 → 문구 수정 (`**단어**` 로 강조)
- 레이아웃: cover / statement / stat / list / compare / cta
- 모델 변경: `CARDNEWS_MODEL=...`
