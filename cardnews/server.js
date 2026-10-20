// 카드뉴스 생성기 서버 — 외부 패키지 없이 Node 18+ 만으로 동작
const http = require("http");
const fs = require("fs");
const path = require("path");

const PORT = process.env.PORT || 3000;
const API_KEY = process.env.ANTHROPIC_API_KEY;
const MODEL = process.env.CARDNEWS_MODEL || "claude-sonnet-5-5";
const PUBLIC = path.join(__dirname, "public");
const MIME = { ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8" };

const SYSTEM = `당신은 인스타그램 카드뉴스 전문 에디터입니다. 주제를 받으면 정확히 10장짜리 카드뉴스를 JSON으로만 출력합니다.

구성 규칙:
- 1번 카드: layout "cover" (후킹 질문형 제목)
- 2~9번 카드: 아래 layout을 섞어서 사용 (문제제기 → 근거/사례 → 핵심 정리 → 실천법 흐름)
- 10번 카드: layout "cta" (행동 유도·마무리)

layout 종류와 필드:
- "cover": kicker(짧은 배지 문구), title(2줄 이내), emoji
- "statement": kicker(작은 도입 문장), title(강한 한 문장, 2~3줄), body(2~3문장 설명), emoji
- "list": title, items(3~5개, 각 25자 이내), body(마무리 한 줄)
- "stat": kicker, number(예: "73%", "3배", "5가지"), title(숫자 설명), body(출처나 부연, 모르는 수치는 지어내지 말고 일반적 서술로)
- "compare": title, left{label, items[2~3]}, right{label, items[2~3]}, body(한 줄 결론)
- "cta": kicker, title, items(1~3개 행동 제안), body(마무리 한 줄), emoji

공통 규칙:
- title/kicker/body/items 안에서 강조할 핵심 단어는 **이렇게** 감싸세요 (카드당 1~2곳).
- 문장은 짧고 임팩트 있게. 한 카드에 글이 너무 많으면 안 됩니다. 글자 수 상한(공백 포함):
  cover title 22자, statement title 18자·body 70자, list title 22자·item 각 22자·body 30자,
  stat number 6자·title 20자·body 30자, compare title 22자·label 8자·item 각 14자·body 28자,
  cta title 22자·item 각 20자·body 24자, kicker 20자.
- 사실 확인이 안 되는 통계·인용·기관명은 만들어내지 마세요.
- emoji는 내용과 어울리는 이모지 1개.
- 출력은 {"cards":[...10개...]} 형태의 JSON 하나뿐. 설명·코드블록 금지.`;

function extractJson(text) {
  const s = text.indexOf("{"), e = text.lastIndexOf("}");
  if (s < 0 || e < 0) throw new Error("모델 응답에서 JSON을 찾지 못했습니다.");
  return JSON.parse(text.slice(s, e + 1));
}

async function generate({ topic, audience, tone }) {
  const user = `주제: ${topic}\n대상 독자: ${audience || "일반 대중"}\n말투: ${tone || "친근하고 명확한 존댓말"}\n\n10장 카드뉴스를 만들어주세요.`;
  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: { "content-type": "application/json", "x-api-key": API_KEY, "anthropic-version": "2023-06-01" },
    body: JSON.stringify({ model: MODEL, max_tokens: 4000, system: SYSTEM, messages: [{ role: "user", content: user }] }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error?.message || `API 오류 ${res.status}`);
  const cards = extractJson(data.content.map((b) => b.text || "").join("")).cards;
  if (!Array.isArray(cards) || cards.length < 2) throw new Error("카드 생성 결과가 올바르지 않습니다.");
  return cards.slice(0, 10);
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    let buf = "";
    req.on("data", (c) => { buf += c; if (buf.length > 1e5) req.destroy(); });
    req.on("end", () => { try { resolve(JSON.parse(buf || "{}")); } catch (e) { reject(e); } });
  });
}

http.createServer(async (req, res) => {
  try {
    if (req.method === "POST" && req.url === "/api/generate") {
      const body = await readBody(req);
      if (!body.topic || !String(body.topic).trim()) throw new Error("주제를 입력해주세요.");
      if (!API_KEY) { res.writeHead(503, { "content-type": "application/json" }); return res.end(JSON.stringify({ error: "NO_KEY" })); }
      const cards = await generate(body);
      res.writeHead(200, { "content-type": "application/json" });
      return res.end(JSON.stringify({ cards }));
    }
    const file = path.join(PUBLIC, req.url === "/" ? "index.html" : path.normalize(req.url.split("?")[0]));
    if (!file.startsWith(PUBLIC) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404); return res.end("Not found"); }
    res.writeHead(200, { "content-type": MIME[path.extname(file)] || "application/octet-stream" });
    fs.createReadStream(file).pipe(res);
  } catch (e) {
    res.writeHead(500, { "content-type": "application/json" });
    res.end(JSON.stringify({ error: e.message }));
  }
}).listen(PORT, () => console.log(`카드뉴스 생성기: http://localhost:${PORT}  (API 키 ${API_KEY ? "설정됨" : "없음 → 데모 모드"})`));
