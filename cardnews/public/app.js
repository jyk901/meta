const $ = (id) => document.getElementById(id);
let cards = [];
let meta = { brand: "", theme: "sky" };
let chars = ["character.png"]; // 기본 캐릭터. 파일을 업로드하면 교체됨

const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
// **강조** → <b>, 줄바꿈 유지
const fmt = (s) => esc(s).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>").replace(/\n/g, "<br>");

const DEMO = [
  { layout: "cover", kicker: "꼭 체크해야 될 **활용법**!", title: "AI가 알려준 답\n**정말 맞을까?**", emoji: "🤖" },
  { layout: "statement", kicker: "AI는 똑똑하지만", title: "**완벽하지** 않습니다", body: "AI는 정확한 답을 찾는 것이 아니라 **가장 가능성 높은 답**을 예측하기 때문에 오류가 발생할 수 있습니다.", emoji: "😵" },
  { layout: "stat", kicker: "환각 효과", number: "3가지", title: "AI가 틀리는 대표 이유", body: "환각 · 맥락 오류 · 편향" },
  { layout: "list", title: "AI 시대에 필요한 건 **판단하는 능력**", items: ["AI의 답을 그대로 믿지 않기", "**출처**를 확인하고 검증하기", "상황에 맞게 판단하고 활용하기"], body: "AI를 **검증**하고 **활용**하는 사람" },
  { layout: "compare", title: "AI를 쓰는 사람 vs **활용하는 사람**", left: { label: "그냥 쓰는 사람", items: ["답을 그대로 복사", "출처 확인 안 함"] }, right: { label: "잘 쓰는 사람", items: ["사실 여부 검증", "수정·보완해서 사용"] }, body: "AI의 답은 정답이 아니라 **초안**입니다." },
  { layout: "statement", kicker: "질문이 달라지면", title: "**답**이 달라집니다", body: "원하는 결과를 이끌어내는 **질문 능력**이 AI 활용의 출발점입니다.", emoji: "💬" },
  { layout: "list", title: "AI 활용 **체크리스트**", items: ["목적에 맞는 AI 선택", "답변의 사실 여부 검증", "결과 수정·보완", "여러 정보를 종합해 최종 판단"], body: "검증하고 보완할 때 **비로소 실무**에서 쓸 수 있어요" },
  { layout: "stat", kicker: "핵심 한 줄", number: "초안", title: "AI의 답은 정답이 아니에요", body: "검증과 보완을 거쳐야 완성됩니다" },
  { layout: "compare", title: "이렇게 **다릅니다**", left: { label: "Before", items: ["AI 답만 믿는다", "오류를 놓친다"] }, right: { label: "After", items: ["출처로 교차 확인", "근거 있게 활용"] }, body: "판단하는 사람이 **AI를 이깁니다**" },
  { layout: "cta", kicker: "AI를 사용하는 사람이 아닌", title: "AI를 **활용하는** 사람으로!", items: ["저장해두고 체크리스트로 활용", "친구에게 공유하기"], body: "그 시작을 함께 하세요!", emoji: "🙌" },
];

function cardHTML(c, i) {
  const pg = `<div class="brand"><i></i>${esc(meta.brand)}</div><div class="pg">${i + 1}/${cards.length}</div>`;
  const kick = c.kicker ? `<div class="kick">${fmt(c.kicker)}</div>` : "";
  const emoji = chars.length ? `<div class="emoji"><img src="${chars[i % chars.length]}"></div>` : c.emoji ? `<div class="emoji">${esc(c.emoji)}</div>` : "";
  const mascot = chars.length ? `<div class="emoji mascot"><img src="${chars[i % chars.length]}"></div>` : "";
  const body = c.body ? `<div class="body">${fmt(c.body)}</div>` : "";
  const items = (a) => (a || []).map((t) => `<div class="it">${fmt(t)}</div>`).join("");
  let inner;
  switch (c.layout) {
    case "cover":
      inner = `<div class="h">${fmt(c.title)}</div>${kick}${emoji}`; break;
    case "list":
      inner = `<div class="h">${fmt(c.title)}</div><div class="box">${items(c.items)}</div>${body}${mascot}`; break;
    case "stat":
      inner = `${kick}<div class="num">${esc(c.number)}</div><div class="h">${fmt(c.title)}</div>${body}${mascot}`; break;
    case "compare": {
      const col = (x, cls) => `<div class="col ${cls}"><strong>${esc(x?.label)}</strong>${(x?.items || []).map((t) => `<p>• ${fmt(t)}</p>`).join("")}</div>`;
      inner = `<div class="h">${fmt(c.title)}</div><div class="cols">${col(c.left, "l")}${col(c.right, "r")}</div>${body}${mascot}`; break;
    }
    case "cta":
      inner = `${kick}<div class="h">${fmt(c.title)}</div><div class="btns">${(c.items || []).map((t) => `<div class="btn">${fmt(t)}</div>`).join("")}</div>${body}${emoji}`; break;
    default:
      c = { ...c, layout: "statement" };
      inner = `${kick}<div class="h">${fmt(c.title)}</div>${emoji}<div class="bodybox">${body}</div>`;
  }
  return `<div class="card ${c.layout} ${meta.theme}${chars.length ? " hasm" : ""}" data-i="${i}">${pg}${inner}</div>`;
}


// ───── 글이 넘치면 글자 크기를 줄여 카드 안에 맞춤 ─────
const TEXT_SEL = ".h,.kick,.body,.num,.it,.btn,.col p,.col strong";
function overflows(card) {
  const scale = card.getBoundingClientRect().width / 1080;
  const top = card.getBoundingClientRect().top;
  const y = (el, edge) => (el.getBoundingClientRect()[edge] - top) / scale;
  const q = (sel) => card.querySelector(sel);
  const layout = [...card.classList].find((c) => ["cover", "statement", "list", "stat", "compare", "cta"].includes(c));
  const hasm = card.classList.contains("hasm");
  const gap = 24;
  // 가로로 삐져나온 글
  for (const el of card.querySelectorAll(".h,.it,.btn,.col p,.num,.kick")) if (el.scrollWidth > el.clientWidth + 1) return true;
  const h = q(".h"), body = q(".body"), box = q(".box") || q(".cols") || q(".btns");
  if (h && y(h, "bottom") > 1290) return true;
  if (layout === "cover" && q(".kick") && y(q(".kick"), "bottom") > (q(".emoji") ? 800 : 1250)) return true;
  if (layout === "statement") {
    const bb = q(".bodybox");
    if (h && y(h, "bottom") > y(bb, "top") - gap) return true;
    if (body && body.offsetHeight > bb.clientHeight - 100) return true;
  }
  if (layout === "list" || layout === "compare" || layout === "cta") {
    if (box && body && y(box, "bottom") > y(body, "top") - gap) return true;
    if (box && hasm && layout !== "cta" && y(box, "bottom") > 950) return true;
  }
  if (layout === "stat" && h && body && y(h, "bottom") > y(body, "top") - gap) return true;
  return false;
}
function fit(card) {
  const els = [...card.querySelectorAll(TEXT_SEL)];
  const base = els.map((el) => parseFloat(getComputedStyle(el).fontSize));
  for (let f = 1; f >= 0.5; f -= 0.04) {
    els.forEach((el, i) => (el.style.fontSize = base[i] * f + "px"));
    if (!overflows(card)) return;
  }
}
const fitAll = () => document.fonts.ready.then(() => document.querySelectorAll("#grid .card").forEach(fit));

function render() {
  $("grid").innerHTML = cards
    .map((c, i) => `<div class="thumb" data-i="${i}">${cardHTML(c, i)}</div>`)
    .join("");
  $("count").textContent = `${cards.length}장 완성`;
  $("result").hidden = false;
  fitAll();
}

const FIELDS = [["kicker", "작은 문구"], ["title", "제목"], ["number", "큰 숫자"], ["body", "본문"], ["items", "항목 (줄바꿈으로 구분)"]];
let editing = -1;

function openEditor(i) {
  editing = i;
  const c = cards[i];
  $("editTitle").textContent = `${i + 1}번 카드 · ${c.layout}`;
  $("fields").innerHTML = FIELDS.filter(([k]) => k in c || k === "title")
    .map(([k, label]) => {
      const v = Array.isArray(c[k]) ? c[k].join("\n") : c[k] ?? "";
      return `<label>${label}<textarea data-k="${k}" rows="${k === "title" || k === "body" || k === "items" ? 3 : 1}">${esc(v)}</textarea></label>`;
    }).join("");
  $("editor").showModal();
}

$("fields").addEventListener("input", (e) => {
  const k = e.target.dataset.k;
  if (!k || editing < 0) return;
  cards[editing][k] = k === "items" ? e.target.value.split("\n").filter(Boolean) : e.target.value;
  const th = document.querySelector(`.thumb[data-i="${editing}"]`);
  th.querySelector(".card").outerHTML = cardHTML(cards[editing], editing);
  fit(th.querySelector(".card"));
});

$("grid").addEventListener("click", (e) => {
  const t = e.target.closest(".thumb");
  if (t) openEditor(+t.dataset.i);
});

async function toPng(i) {
  await document.fonts.ready;
  const el = document.querySelector(`.thumb[data-i="${i}"] .card`);
  return htmlToImage.toPng(el, { width: 1080, height: 1350, pixelRatio: 1, style: { transform: "none" } });
}
function save(url, name) {
  const a = document.createElement("a");
  a.href = url; a.download = name; a.click();
}
$("dlOne").onclick = async () => save(await toPng(editing), `cardnews-${String(editing + 1).padStart(2, "0")}.png`);
$("dlAll").onclick = async (e) => {
  e.target.disabled = true;
  for (let i = 0; i < cards.length; i++) {
    e.target.textContent = `저장 중 ${i + 1}/${cards.length}`;
    save(await toPng(i), `cardnews-${String(i + 1).padStart(2, "0")}.png`);
    await new Promise((r) => setTimeout(r, 250));
  }
  e.target.textContent = "전체 PNG 저장";
  e.target.disabled = false;
};

$("chars").addEventListener("change", async (e) => {
  chars = await Promise.all([...e.target.files].map((f) => new Promise((ok) => {
    const r = new FileReader(); r.onload = () => ok(r.result); r.readAsDataURL(f);
  })));
  if (!chars.length) chars = ["character.png"];
  if (cards.length) render();
});

function say(text) { $("msg").textContent = text; $("msg").hidden = !text; }

$("form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const btn = $("go");
  btn.disabled = true; btn.textContent = "만드는 중… (10~30초)"; say("");
  meta = { brand: $("brand").value || "My Brand", theme: $("theme").value };
  try {
    const r = await fetch("/api/generate", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ topic: $("topic").value, audience: $("audience").value, tone: $("tone").value }),
    });
    const data = await r.json();
    if (data.error === "NO_KEY") {
      cards = structuredClone(DEMO);
      say("서버에 ANTHROPIC_API_KEY가 없어 샘플 카드를 보여드려요. 키를 설정하면 입력한 주제로 생성됩니다.");
    } else if (!r.ok) throw new Error(data.error);
    else cards = data.cards;
    render();
  } catch (err) {
    say("오류: " + err.message);
  } finally {
    btn.disabled = false; btn.textContent = "카드뉴스 만들기";
  }
});
