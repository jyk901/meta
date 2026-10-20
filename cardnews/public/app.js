const $ = (id) => document.getElementById(id);
let cards = [];
let meta = { brand: "", theme: "sky" };
let chars = ["character.png"]; // 기본 캐릭터. 파일을 업로드하면 교체됨

const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
// **강조** → <b>, 줄바꿈 유지
const fmt = (s) => esc(s).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>").replace(/\n/g, "<br>");

const DEMO = [
  { layout: "cover", kicker: "꼭 체크할 **활용법**", title: "AI 답, **정말** 맞을까?", illus: ["🤖", "❓"] },
  { layout: "statement", kicker: "AI는 똑똑하지만", title: "**완벽**하지 않아요", body: "가장 **그럴듯한 답**을 예측할 뿐이에요", illus: ["🎲"] },
  { layout: "stat", kicker: "AI가 틀리는 이유", number: "3가지", title: "환각·맥락·편향", illus: ["⚠️", "🧩"] },
  { layout: "list", title: "AI 쓸 때 **체크**", items: ["그대로 믿지 않기", "**출처** 확인하기", "상황에 맞게 판단"], illus: ["✅", "🔍"] },
  { layout: "compare", title: "쓰기만 vs **활용하기**", left: { label: "쓰기만", items: ["그대로 복사", "출처 무시"] }, right: { label: "활용", items: ["사실 검증", "수정·보완"] }, illus: ["⚖️"] },
  { layout: "statement", kicker: "질문이 달라지면", title: "**답**이 달라져요", body: "좋은 질문이 좋은 결과를 만들어요", illus: ["💬", "✨"] },
  { layout: "list", title: "AI 활용 **3단계**", items: ["목적에 맞는 AI 고르기", "사실 여부 검증", "수정하고 보완"], illus: ["🧰", "📝"] },
  { layout: "stat", kicker: "기억할 한 단어", number: "초안", title: "AI의 답은 정답이 아니에요", illus: ["✏️", "📄"] },
  { layout: "compare", title: "이렇게 **다릅니다**", left: { label: "Before", items: ["AI 답만 믿음", "오류를 놓침"] }, right: { label: "After", items: ["출처로 확인", "근거 있게 활용"] }, illus: ["🔄"] },
  { layout: "cta", kicker: "AI를 쓰는 사람에서", title: "AI를 **활용하는** 사람으로!", items: ["저장해두기", "친구에게 공유"], illus: ["🚀", "🙌"] },
];

// 캐릭터를 넣을지: 카드별 설정(c.char)이 있으면 그것, 없으면 전체 설정을 따름
const showChar = (c) => chars.length > 0 && (c.char ?? $("useChar").value === "on");

function cardHTML(c, i) {
  const on = showChar(c);
  const pg = `<div class="brand"><i></i>${esc(meta.brand)}</div><div class="pg">${i + 1}/${cards.length}</div>`;
  const kick = c.kicker ? `<div class="kick">${fmt(c.kicker)}</div>` : "";
  const person = on ? `<div class="emoji"><img src="${chars[i % chars.length]}"></div>` : "";
  const mascot = on ? `<div class="emoji mascot"><img src="${chars[i % chars.length]}"></div>` : "";
  const list = (Array.isArray(c.illus) ? c.illus : c.illus ? [c.illus] : c.emoji ? [c.emoji] : []).slice(0, 2);
  const illus = list.length ? `<div class="illus">${list.map((e) => `<span>${esc(e)}</span>`).join("")}</div>` : "";
  const body = c.body ? `<div class="body">${fmt(c.body)}</div>` : "";
  const items = (a) => (a || []).map((t) => `<div class="it">${fmt(t)}</div>`).join("");
  let inner;
  switch (c.layout) {
    case "cover":
      inner = `<div class="h">${fmt(c.title)}</div>${kick}${illus}${person}`; break;
    case "list":
      inner = `<div class="h">${fmt(c.title)}</div><div class="box">${items(c.items)}</div>${illus}${mascot}`; break;
    case "stat":
      inner = `${kick}<div class="num">${esc(c.number)}</div><div class="h">${fmt(c.title)}</div>${illus}${mascot}`; break;
    case "compare": {
      const col = (x, cls) => `<div class="col ${cls}"><strong>${esc(x?.label)}</strong>${(x?.items || []).map((t) => `<p>• ${fmt(t)}</p>`).join("")}</div>`;
      inner = `<div class="h">${fmt(c.title)}</div><div class="cols">${col(c.left, "l")}${col(c.right, "r")}</div>${illus}${mascot}`; break;
    }
    case "cta":
      inner = `${kick}<div class="h">${fmt(c.title)}</div><div class="btns">${(c.items || []).map((t) => `<div class="btn">${fmt(t)}</div>`).join("")}</div>${illus}${person}`; break;
    default:
      c = { ...c, layout: "statement" };
      inner = `${kick}<div class="h">${fmt(c.title)}</div>${person}<div class="bodybox">${illus}${body}</div>`;
  }
  return `<div class="card ${c.layout} ${meta.theme}${on ? " hasm" : " nochar"}" data-i="${i}">${pg}${inner}</div>`;
}


// ───── 글이 넘치면 글자 크기를 줄여 카드 안에 맞춤 ─────
const TEXT_SEL = ".h,.kick,.body,.num,.it,.btn,.col p,.col strong";
function overflows(card) {
  const scale = card.getBoundingClientRect().width / 1080;
  const top = card.getBoundingClientRect().top;
  const y = (el, edge) => (el.getBoundingClientRect()[edge] - top) / scale;
  const q = (sel) => card.querySelector(sel);
  const layout = [...card.classList].find((c) => ["cover", "statement", "list", "stat", "compare", "cta"].includes(c));
  const gap = 24;
  // 가로로 삐져나온 글
  for (const el of card.querySelectorAll(".h,.it,.btn,.col p,.num,.kick")) if (el.scrollWidth > el.clientWidth + 1) return true;
  const h = q(".h"), body = q(".body"), illus = q(".illus");
  if (h && y(h, "bottom") > 1290) return true;
  if (layout === "cover" && q(".kick") && y(q(".kick"), "bottom") > (q(".emoji") || q(".illus") ? 750 : 1250)) return true;
  if (layout === "statement") {
    const bb = q(".bodybox");
    if (h && y(h, "bottom") > y(bb, "top") - gap) return true;
    if (body && body.offsetHeight > bb.clientHeight - 120) return true;
  }
  // 아래쪽 그림·캐릭터 띠(약 940px부터) 위에서 글이 끝나야 함
  if (layout === "list" || layout === "compare" || layout === "cta" || layout === "stat") {
    const last = layout === "stat" ? h : q(".box") || q(".cols") || q(".btns");
    const limit = illus ? Math.min(y(illus, "top") - gap, 940) : 1290;
    if (last && y(last, "bottom") > limit) return true;
  }
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

const FIELDS = [["kicker", "작은 문구"], ["title", "제목"], ["number", "큰 숫자"], ["body", "본문"], ["items", "항목 (줄바꿈으로 구분)"], ["illus", "그림 (이모지 1~2개)"]];
let editing = -1;

function openEditor(i) {
  editing = i;
  const c = cards[i];
  $("editTitle").textContent = `${i + 1}번 카드 · ${c.layout}`;
  $("fields").innerHTML = `<label class="chk"><input type="checkbox" data-k="char" ${showChar(c) ? "checked" : ""}> 이 카드에 캐릭터 넣기</label>` + FIELDS.filter(([k]) => k in c || k === "title" || k === "illus")
    .map(([k, label]) => {
      const v = Array.isArray(c[k]) ? c[k].join(k === "illus" ? "" : "\n") : c[k] ?? "";
      return `<label>${label}<textarea data-k="${k}" rows="${k === "title" || k === "body" || k === "items" ? 3 : 1}">${esc(v)}</textarea></label>`;
    }).join("");
  $("editor").showModal();
}

$("fields").addEventListener("input", (e) => {
  const k = e.target.dataset.k;
  if (!k || editing < 0) return;
  if (k === "char") cards[editing].char = e.target.checked;
  else cards[editing][k] = k === "items" ? e.target.value.split("\n").filter(Boolean) : k === "illus" ? [...new Intl.Segmenter().segment(e.target.value.replace(/\s/g, ""))].map((x) => x.segment).slice(0, 2) : e.target.value;
  const th = document.querySelector(`.thumb[data-i="${editing}"]`);
  th.querySelector(".card").outerHTML = cardHTML(cards[editing], editing);
  fit(th.querySelector(".card"));
});

$("useChar").addEventListener("change", () => {
  cards.forEach((c) => delete c.char);
  if (cards.length) render();
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
