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

핵심 원칙: 글은 최소한으로, 그림은 크게. 카드 한 장에는 한 가지 메시지만 담습니다. 설명하려 하지 말고 한눈에 읽히게 쓰세요.

구성:
- 1번 카드: layout "cover" (호기심을 자극하는 질문형 제목)
- 2~9번 카드: 아래 layout을 섞어서 사용 (문제제기 → 근거/사례 → 핵심 정리 → 실천법 흐름)
- 10번 카드: layout "cta" (행동 유도·마무리)

layout과 필드 (글자 수는 공백 포함 상한이며 반드시 지키세요):
- "cover": kicker(14자), title(16자), illus(이모지 2개)
- "statement": kicker(14자), title(14자), body(36자, 한 문장), illus(이모지 1~2개)
- "list": title(16자), items(정확히 3개, 각 14자), illus
- "stat": kicker(14자), number(6자, 예: "73%", "3배", "5가지"), title(16자), illus
- "compare": title(16자), left{label(6자), items(2개, 각 10자)}, right{label, items 동일}, illus
- "cta": kicker(14자), title(16자), items(2개, 각 14자), illus

illus는 카드 내용을 한눈에 보여주는 이모지 배열입니다.
- 표정 이모지보다 주제를 설명하는 사물·장면 이모지를 고르세요. 예: 건강 → ["🥗","🏃"], 돈 → ["💰","📈"], 학교 → ["🏫","📚"].
- 카드마다 서로 다른 이모지를 쓰고, 그 카드의 title 내용과 직접 관련되어야 합니다.

공통 규칙:
- 강조할 핵심 단어는 **이렇게** 감싸세요 (카드당 1곳 이하).
- 사실 확인이 안 되는 통계·인용·기관명은 만들어내지 마세요.
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
