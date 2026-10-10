const API = window.API_BASE_URL.replace(/\/$/, "");
const SLOW_NOTICE_MS = 5000;
const SLOW_NOTICE = "서버를 깨우는 중이에요. 무료 서버라 첫 요청은 최대 1분쯤 걸릴 수 있어요.";

const $ = (id) => document.getElementById(id);
const state = { conversationId: null, editingId: null, data: [] };

// ── 공통 ────────────────────────────────────────────────
// slowNotice: 응답이 늦을 때 '서버 깨우는 중' 안내를 띄울지. (채팅은 말풍선으로 따로 안내하므로 끈다)
async function api(path, { slowNotice = true, ...options } = {}) {
  const slowTimer = slowNotice && setTimeout(() => showNotice(SLOW_NOTICE), SLOW_NOTICE_MS);
  try {
    const response = await fetch(API + path, {
      ...options,
      headers: options.body ? { "Content-Type": "application/json" } : undefined,
    });
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new Error(typeof body.detail === "string" ? body.detail : "입력 값을 확인해 주세요.");
    }
    hideNotice();
    return response.status === 204 ? null : response.json();
  } catch (error) {
    if (error instanceof TypeError) throw new Error("서버에 연결하지 못했어요. 잠시 후 다시 시도해 주세요.");
    throw error;
  } finally {
    clearTimeout(slowTimer);
  }
}

function showNotice(text, isError = false) {
  $("notice").textContent = text;
  $("notice").classList.toggle("error", isError);
  $("notice").hidden = false;
}

function hideNotice() {
  $("notice").hidden = true;
}

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

// ── 탭 ─────────────────────────────────────────────────
function showTab(name) {
  document.querySelectorAll(".tab").forEach((tab) => tab.classList.toggle("active", tab.dataset.tab === name));
  ["chat", "data", "history"].forEach((tab) => { $(`tab-${tab}`).hidden = tab !== name; });
}

document.querySelectorAll(".tab").forEach((tab) => tab.addEventListener("click", () => showTab(tab.dataset.tab)));

// ── 데이터 요약 ─────────────────────────────────────────
async function loadSummary() {
  const summary = await api("/api/data/summary");
  const metrics = summary.metrics;
  $("sum-period").textContent = summary.period ?? "–";
  $("sum-count").textContent = `${summary.count}개`;
  $("sum-average").textContent = metrics ? `${metrics.average}℃` : "–";
  $("sum-max").textContent = metrics ? `${metrics.max}℃ (${metrics.max_date.slice(0, 7)})` : "–";
  $("sum-min").textContent = metrics ? `${metrics.min}℃ (${metrics.min_date.slice(0, 7)})` : "–";
  $("sum-trend").textContent = summary.trend;
}

// ── 채팅 ───────────────────────────────────────────────
// AI 답변의 **굵게** 표시만 안전하게 바꿔 보여준다. (HTML로 해석하지 않음)
function fillWithBold(node, text) {
  text.split("**").forEach((part, index) => {
    node.append(index % 2 ? element("strong", "", part) : part);
  });
}

function addBubble(role, text) {
  $("messages").querySelector(".empty")?.remove();
  const bubble = element("div", `bubble ${role}`);
  fillWithBold(bubble, text);
  $("messages").append(bubble);
  $("messages").scrollTop = $("messages").scrollHeight;
  return bubble;
}

function renderMessages(messages) {
  $("messages").replaceChildren();
  if (!messages.length) {
    $("messages").append(element("p", "empty", "데이터에 대해 궁금한 것을 물어보세요."));
  }
  messages.forEach((message) => addBubble(message.role, message.content));
}

function startNewChat() {
  state.conversationId = null;
  $("chat-title").textContent = "새 대화";
  renderMessages([]);
  $("chat-input").focus();
}

$("new-chat").addEventListener("click", startNewChat);

$("chat-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = $("chat-input").value.trim();
  if (!message) return;

  $("chat-input").value = "";
  addBubble("user", message);
  const loading = addBubble("assistant", "답변을 작성하는 중");
  loading.classList.add("loading");
  $("chat-form").querySelector("button").disabled = true;

  try {
    const result = await api("/api/chat", {
      method: "POST",
      body: JSON.stringify({ message, conversation_id: state.conversationId }),
      slowNotice: false,
    });
    loading.remove();
    addBubble("assistant", result.reply);
    if (!state.conversationId) $("chat-title").textContent = message.slice(0, 30);
    state.conversationId = result.conversation_id;
    loadHistory();
  } catch (error) {
    loading.remove();
    showNotice(error.message, true);
  } finally {
    $("chat-form").querySelector("button").disabled = false;
    $("chat-input").focus();
  }
});

// ── 데이터 관리 ─────────────────────────────────────────
async function loadData() {
  state.data = (await api("/api/data")).reverse();   // 최신 날짜가 위로
  renderData();
}

function renderData() {
  $("data-rows").replaceChildren(...state.data.map((item) => {
    const row = element("tr", item.id === state.editingId ? "editing" : "");
    const actions = element("td", "actions");
    const edit = element("button", "ghost small", "수정");
    const remove = element("button", "ghost small danger", "삭제");
    edit.addEventListener("click", () => startEdit(item));
    remove.addEventListener("click", () => removeData(item));
    actions.append(edit, " ", remove);
    row.append(element("td", "", item.date), element("td", "num", item.value), element("td", "", item.memo), actions);
    return row;
  }));
}

function startEdit(item) {
  state.editingId = item.id;
  $("data-date").value = item.date;
  $("data-value").value = item.value;
  $("data-memo").value = item.memo;
  $("data-form-title").textContent = `데이터 수정 (${item.date})`;
  $("data-submit").textContent = "저장";
  $("data-cancel").hidden = false;
  renderData();
  $("data-value").focus();
}

function resetDataForm() {
  state.editingId = null;
  $("data-form").reset();
  $("data-form-title").textContent = "새 데이터 추가";
  $("data-submit").textContent = "추가";
  $("data-cancel").hidden = true;
  renderData();
}

$("data-cancel").addEventListener("click", resetDataForm);

$("data-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const body = JSON.stringify({
    date: $("data-date").value,
    value: Number($("data-value").value),
    memo: $("data-memo").value.trim(),
  });
  try {
    if (state.editingId) {
      await api(`/api/data/${state.editingId}`, { method: "PUT", body });
    } else {
      await api("/api/data", { method: "POST", body });
    }
    resetDataForm();
    await Promise.all([loadData(), loadSummary()]);
  } catch (error) {
    showNotice(error.message, true);
  }
});

async function removeData(item) {
  if (!confirm(`${item.date} 데이터를 삭제할까요?`)) return;
  try {
    await api(`/api/data/${item.id}`, { method: "DELETE" });
    if (state.editingId === item.id) resetDataForm();
    await Promise.all([loadData(), loadSummary()]);
  } catch (error) {
    showNotice(error.message, true);
  }
}

// ── 대화 기록 ───────────────────────────────────────────
async function loadHistory() {
  const conversations = await api("/api/conversations");
  if (!conversations.length) {
    $("history-list").replaceChildren(element("li", "", "아직 저장된 대화가 없어요."));
    return;
  }
  $("history-list").replaceChildren(...conversations.map((conversation) => {
    const item = element("li", conversation.id === state.conversationId ? "current" : "");
    const info = element("div", "info");
    const updated = new Date(conversation.updated_at).toLocaleString("ko-KR", { dateStyle: "short", timeStyle: "short" });
    info.append(element("div", "title", conversation.title),
                element("div", "meta", `${updated} · 메시지 ${conversation.message_count}개`));
    const open = element("button", "small", "불러오기");
    const remove = element("button", "ghost small danger", "삭제");
    open.addEventListener("click", () => openConversation(conversation.id));
    remove.addEventListener("click", () => removeConversation(conversation));
    item.append(info, open, remove);
    return item;
  }));
}

async function openConversation(id) {
  try {
    const conversation = await api(`/api/conversations/${id}`);
    state.conversationId = conversation.id;
    $("chat-title").textContent = conversation.title;
    renderMessages(conversation.messages);
    showTab("chat");
    loadHistory();
  } catch (error) {
    showNotice(error.message, true);
  }
}

async function removeConversation(conversation) {
  if (!confirm(`"${conversation.title}" 대화를 삭제할까요?`)) return;
  try {
    await api(`/api/conversations/${conversation.id}`, { method: "DELETE" });
    if (state.conversationId === conversation.id) startNewChat();
    await loadHistory();
  } catch (error) {
    showNotice(error.message, true);
  }
}

// ── 시작 ───────────────────────────────────────────────
renderMessages([]);
Promise.all([loadSummary(), loadData(), loadHistory()]).catch((error) => showNotice(error.message, true));
