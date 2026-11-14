"use strict";

// La conversación vive solo en el navegador: se envían al servidor los últimos turnos
// para que el bot entienda preguntas de seguimiento.
const HISTORY_ITEMS = 12;
const history = [];
let busy = false;
let msgCount = 0;

const hilo = document.getElementById("hilo");
const form = document.getElementById("formulario");
const input = document.getElementById("mensaje");
const sendBtn = document.getElementById("enviar");
const intro = document.getElementById("intro");
const estado = document.getElementById("estado");

// ---------- Utilidades de render ----------

function escapeHtml(text) {
  return text.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
}

function inline(text, msgId) {
  return escapeHtml(text)
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/(^|[^*])\*([^*\s][^*]*?)\*/g, "$1<em>$2</em>")
    .replace(/\[(\d+(?:\s*,\s*\d+)*)\]/g, (_, group) =>
      group.split(/\s*,\s*/).map((n) => `<a class="cite" href="#src-${msgId}-${n}" data-n="${n}">${n}</a>`).join("")
    );
}

// Markdown mínimo y seguro: párrafos, listas, negrita, cursiva y citas [n].
function renderMarkdown(text, msgId) {
  const lines = text.replace(/\r/g, "").split("\n");
  let html = "";
  let list = null;
  let para = [];
  const flushPara = () => {
    if (para.length) html += `<p>${inline(para.join(" "), msgId)}</p>`;
    para = [];
  };
  const closeList = () => {
    if (list) html += `</${list}>`;
    list = null;
  };
  for (const raw of lines) {
    const line = raw.trim();
    const ul = line.match(/^[-*•]\s+(.*)$/);
    const ol = line.match(/^\d+[.)]\s+(.*)$/);
    const heading = line.match(/^#{1,6}\s+(.*)$/);
    if (ul || ol) {
      flushPara();
      const kind = ul ? "ul" : "ol";
      if (list !== kind) { closeList(); html += `<${kind}>`; list = kind; }
      html += `<li>${inline((ul || ol)[1], msgId)}</li>`;
    } else if (!line) {
      flushPara(); closeList();
    } else if (heading) {
      flushPara(); closeList();
      html += `<p><strong>${inline(heading[1], msgId)}</strong></p>`;
    } else {
      closeList();
      para.push(line);
    }
  }
  flushPara(); closeList();
  return html;
}

function el(tag, className, html) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (html !== undefined) node.innerHTML = html;
  return node;
}

function scrollToEnd() {
  window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
}

// ---------- Fuentes ----------

const VIGENCIA_LABEL = { modificada: "Modificada", derogada: "Derogada", por_verificar: "Vigencia por verificar" };

function sourceItem(src, msgId) {
  const li = el("li", "src");
  li.id = `src-${msgId}-${src.n}`;
  const badge = VIGENCIA_LABEL[src.vigencia]
    ? `<span class="badge" title="${escapeHtml(src.nota_vigencia || "")}">${VIGENCIA_LABEL[src.vigencia]}</span>`
    : "";
  const links = [
    src.url ? `<a href="${escapeHtml(src.url)}" target="_blank" rel="noopener">Fuente original ↗</a>` : "",
    src.pdf_url ? `<a href="${encodeURI(src.pdf_url)}" target="_blank" rel="noopener">PDF del corpus ↗</a>` : "",
  ].join("");
  li.innerHTML = `
    <div class="src-head">
      <span class="src-n">[${src.n}]</span>
      <span class="src-cita">${escapeHtml(src.cita)}</span>
      ${badge}
    </div>
    <div class="src-meta">${escapeHtml(src.pais)}${src.seccion ? " · " + escapeHtml(src.seccion) : ""}</div>
    <p class="src-extract">${escapeHtml(src.extracto)}…</p>
    <div class="src-links">${links}</div>`;
  return li;
}

function renderSources(container, sources, cited, msgId) {
  container.innerHTML = "";
  if (!sources.length) return;
  const citedSet = new Set(cited);
  const used = sources.filter((s) => citedSet.has(s.n));
  const others = sources.filter((s) => !citedSet.has(s.n));

  if (used.length) {
    container.append(el("h2", "", "↳ Fuentes citadas"));
    const ul = el("ul", "src-list");
    used.forEach((s) => ul.append(sourceItem(s, msgId)));
    container.append(ul);
  }
  if (others.length) {
    const details = el("details");
    details.append(el("summary", "", `Otros fragmentos consultados (${others.length})`));
    const ul = el("ul", "src-list");
    others.forEach((s) => ul.append(sourceItem(s, msgId)));
    details.append(ul);
    container.append(details);
  }
}

// Al pulsar una cita [n], abrir el bloque que la contiene y resaltar la fuente.
hilo.addEventListener("click", (ev) => {
  const link = ev.target.closest("a.cite");
  if (!link) return;
  const target = document.querySelector(link.getAttribute("href"));
  if (!target) return;
  ev.preventDefault();
  const details = target.closest("details");
  if (details) details.open = true;
  target.scrollIntoView({ behavior: "smooth", block: "center" });
  target.classList.add("flash");
  setTimeout(() => target.classList.remove("flash"), 1500);
});

// ---------- Conversación ----------

function addUserMessage(text) {
  const node = el("div", "msg msg-user");
  node.textContent = text;
  hilo.append(node);
}

function addBotMessage() {
  const msgId = ++msgCount;
  const node = el("article", "msg msg-bot");
  node.setAttribute("aria-label", "Respuesta de DilemaBot");
  const who = el("div", "who", "DilemaBot");
  const body = el("div", "answer pending");
  const notices = el("div");
  const sources = el("div", "sources");
  sources.hidden = true;
  node.append(who, body, notices, sources);
  hilo.append(node);
  return { msgId, body, notices, sources };
}

function notice(container, text, kind = "") {
  container.append(el("div", `notice ${kind}`, escapeHtml(text)));
}

async function* readEvents(response) {
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    let idx;
    while ((idx = buffer.indexOf("\n\n")) >= 0) {
      const chunk = buffer.slice(0, idx);
      buffer = buffer.slice(idx + 2);
      const data = chunk.split("\n").filter((l) => l.startsWith("data:")).map((l) => l.slice(5).trim()).join("");
      if (data) yield JSON.parse(data);
    }
  }
}

async function send(question) {
  if (busy || !question.trim()) return;
  busy = true;
  sendBtn.disabled = true;
  intro.hidden = true;

  addUserMessage(question);
  const ui = addBotMessage();
  scrollToEnd();

  let text = "";
  let sources = [];
  let finished = false;
  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mensaje: question, historial: history.slice(-HISTORY_ITEMS) }),
    });
    if (!response.ok) {
      const detail = await response.json().catch(() => ({}));
      throw new Error(typeof detail.detail === "string" ? detail.detail : `Error ${response.status}`);
    }
    for await (const event of readEvents(response)) {
      if (event.type === "fuentes") {
        sources = event.fuentes || [];
        (event.avisos || []).forEach((a) => notice(ui.notices, a));
        if (sources.length) {
          // En CPU el modelo tarda en leer los fragmentos antes del primer token.
          ui.body.innerHTML = `<p class="thinking">Leyendo ${sources.length} fragmentos del corpus…</p>`;
        }
      } else if (event.type === "token") {
        text += event.text;
        ui.body.innerHTML = renderMarkdown(text, ui.msgId);
      } else if (event.type === "error") {
        notice(ui.notices, event.mensaje, "error");
      } else if (event.type === "fin") {
        finished = true;
        // Quita las citas que no corresponden a ningún fragmento recuperado.
        const invalid = new Set(event.citas_invalidas || []);
        if (invalid.size) {
          text = text.replace(/\[(\d+)\]/g, (m, n) => (invalid.has(Number(n)) ? "" : m));
          notice(ui.notices, "Se eliminaron citas que no correspondían a ninguna fuente recuperada.");
        }
        ui.body.innerHTML = renderMarkdown(text, ui.msgId);
        if (event.sin_citas) notice(ui.notices, "Esta respuesta no incluye citas verificables: tómala con cautela.");
        renderSources(ui.sources, sources, event.citadas || [], ui.msgId);
        ui.sources.hidden = !sources.length;
      }
    }
  } catch (err) {
    notice(ui.notices, `No se pudo obtener respuesta: ${err.message}`, "error");
  } finally {
    ui.body.classList.remove("pending");
    if (!text && !ui.notices.childElementCount) notice(ui.notices, "La respuesta llegó vacía.", "error");
    if (finished && text) {
      history.push({ rol: "usuario", contenido: question }, { rol: "bot", contenido: text });
    }
    busy = false;
    sendBtn.disabled = false;
    input.focus();
    scrollToEnd();
  }
}

form.addEventListener("submit", (ev) => {
  ev.preventDefault();
  const q = input.value;
  input.value = "";
  autoGrow();
  send(q);
});

input.addEventListener("keydown", (ev) => {
  if (ev.key === "Enter" && !ev.shiftKey) {
    ev.preventDefault();
    form.requestSubmit();
  }
});

function autoGrow() {
  input.style.height = "auto";
  input.style.height = `${Math.min(input.scrollHeight, 160)}px`;
}
input.addEventListener("input", autoGrow);

document.getElementById("sugerencias").addEventListener("click", (ev) => {
  const btn = ev.target.closest("button[data-q]");
  if (btn) send(btn.dataset.q);
});

// ---------- Estado del modelo ----------

async function checkHealth() {
  try {
    const res = await fetch("/api/salud");
    const data = await res.json();
    const llm = data.llm || {};
    if (!data.indice.cargado) {
      estado.textContent = "Índice no generado";
      estado.className = "status bad";
    } else if (llm.ok) {
      estado.textContent = `${llm.proveedor} · ${llm.modelo}${data.indice.vectores ? " · híbrida" : " · BM25"}`;
      estado.className = "status ok";
    } else {
      estado.textContent = llm.detalle || "Modelo no disponible";
      estado.className = "status bad";
    }
    estado.title = llm.detalle || "";
  } catch {
    estado.textContent = "Servidor no disponible";
    estado.className = "status bad";
  }
}
checkHealth();
