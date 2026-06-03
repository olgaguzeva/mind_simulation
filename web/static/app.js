/* ── State ───────────────────────────────────────────────── */
let sessionId = null;
let personalityColors = {};
let isStreaming = false;
let _editTarget = null;  // card currently open in the modal

/* ── Init ────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', async () => {
  await loadDefaults();
  updateStartBtn();
});

async function loadDefaults() {
  try {
    const res = await fetch('/api/defaults');
    const defaults = await res.json();
    defaults.forEach(p => addCard(p.name, p.description));
  } catch {
    addCard();
  }
}

/* ── Personality cards ───────────────────────────────────── */
function addCard(name = '', description = '') {
  const list = document.getElementById('personalities-list');
  const card = document.createElement('div');
  card.className = 'p-card';
  card.dataset.name = name;
  card.dataset.description = description;
  card.onclick = () => openEditModal(card);
  card.innerHTML = `
    <div class="p-dot"></div>
    <span class="p-name">${name ? escHtml(name) : '<em class="p-name-empty">Unnamed</em>'}</span>
    <span class="p-edit-icon">✎</span>
  `;
  list.appendChild(card);
  updateStartBtn();
}

function updateStartBtn() {
  const cards = document.querySelectorAll('.p-card');
  const valid = [...cards].some(c => c.dataset.name?.trim() && c.dataset.description?.trim());
  document.getElementById('start-btn').disabled = !valid;
}

function getPersonalities() {
  return [...document.querySelectorAll('.p-card')].map(c => ({
    name: c.dataset.name,
    description: c.dataset.description,
  })).filter(p => p.name && p.description);
}

/* ── Modal ───────────────────────────────────────────────── */
function openEditModal(card) {
  _editTarget = card;
  document.getElementById('modal-name').value = card.dataset.name || '';
  document.getElementById('modal-desc').value = card.dataset.description || '';
  document.getElementById('edit-modal').classList.remove('hidden');
  document.getElementById('modal-name').focus();
}

function closeModal() {
  document.getElementById('edit-modal').classList.add('hidden');
  _editTarget = null;
}

function closeModalOnOverlay(e) {
  if (e.target === document.getElementById('edit-modal')) closeModal();
}

function saveModal() {
  if (!_editTarget) return;
  const name = document.getElementById('modal-name').value.trim();
  const description = document.getElementById('modal-desc').value.trim();
  _editTarget.dataset.name = name;
  _editTarget.dataset.description = description;
  const nameEl = _editTarget.querySelector('.p-name');
  nameEl.innerHTML = name ? escHtml(name) : '<em class="p-name-empty">Unnamed</em>';
  closeModal();
  updateStartBtn();
}

function deleteModalCard() {
  if (!_editTarget) return;
  _editTarget.remove();
  closeModal();
  updateStartBtn();
}

function handleBulkUpload(input) {
  const files = [...input.files];
  files.forEach(file => {
    const reader = new FileReader();
    reader.onload = e => {
      const name = file.name.replace(/\.(txt|md)$/i, '').replace(/^\w/, c => c.toUpperCase());
      const description = e.target.result.trim();
      const existing = [...document.querySelectorAll('.p-card')]
        .find(c => c.dataset.name.toLowerCase() === name.toLowerCase());
      if (existing) {
        existing.dataset.description = description;
      } else {
        addCard(name, description);
      }
    };
    reader.readAsText(file);
  });
  input.value = '';
}

function handleModalFileUpload(input) {
  const file = input.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = e => {
    document.getElementById('modal-desc').value = e.target.result.trim();
  };
  reader.readAsText(file);
  input.value = '';
}

/* ── Session ─────────────────────────────────────────────── */
async function startSession() {
  const personalities = getPersonalities();
  if (!personalities.length) return;

  setLoading(true);
  try {
    const res = await fetch('/api/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ personalities }),
    });
    if (!res.ok) {
      const err = await res.json();
      alert(err.detail || 'Failed to start session.');
      return;
    }
    const data = await res.json();
    sessionId = data.session_id;
    personalityColors = data.personality_colors;
    activateSession();
  } catch {
    alert('Could not connect to server.');
  } finally {
    setLoading(false);
  }
}

function activateSession() {
  lockSidebar();
  buildLegend();
  document.getElementById('empty-state')?.remove();
  document.getElementById('input-area').classList.remove('hidden');
  document.getElementById('download-btn').classList.remove('hidden');
  document.getElementById('message-input').focus();
}

function lockSidebar() {
  document.querySelectorAll('.p-card').forEach(card => {
    card.onclick = null;
    card.classList.add('locked');
    const name = card.dataset.name;
    const color = personalityColors[name];
    if (color) {
      card.classList.add('active');
      card.style.setProperty('--p-color', color);
      card.querySelector('.p-dot').style.background = color;
    }
  });
  document.getElementById('add-btn').style.display = 'none';
  document.getElementById('upload-bulk-btn').style.display = 'none';
  const startBtn = document.getElementById('start-btn');
  startBtn.textContent = '↺ Reset';
  startBtn.disabled = false;
  startBtn.onclick = resetSession;
}

function resetSession() {
  sessionId = null;
  personalityColors = {};
  isStreaming = false;
  _editTarget = null;

  document.querySelectorAll('.p-card').forEach(card => {
    card.classList.remove('locked', 'active');
    card.style.removeProperty('--p-color');
    card.querySelector('.p-dot').style.background = '';
    card.onclick = () => openEditModal(card);
  });

  document.getElementById('add-btn').style.display = '';
  document.getElementById('upload-bulk-btn').style.display = '';
  const startBtn = document.getElementById('start-btn');
  startBtn.textContent = 'Begin session';
  startBtn.onclick = startSession;
  updateStartBtn();

  const messages = document.getElementById('messages');
  messages.innerHTML = `
    <div class="empty-state" id="empty-state">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"/>
        <path d="M12 6v6l4 2"/>
      </svg>
      <p>Define your personalities and begin a session to start the debate.</p>
    </div>`;
  document.getElementById('input-area').classList.add('hidden');
  document.getElementById('download-btn').classList.add('hidden');
  document.getElementById('legend').innerHTML = '';
}

function downloadHistory() {
  const turns = document.querySelectorAll('.turn');
  if (!turns.length) return;

  const lines = ['Mind Simulation — Session Transcript', '='.repeat(52), ''];

  turns.forEach((turn, i) => {
    if (i > 0) lines.push('-'.repeat(52), '');

    const userMsg = turn.querySelector('.user-bubble')?.textContent.trim();
    if (userMsg) lines.push(`You: ${userMsg}`, '');

    turn.querySelectorAll('.round').forEach(round => {
      const label = round.querySelector('.round-label')?.textContent.trim();
      lines.push(`  ${label}:`);
      round.querySelectorAll('.position-card').forEach(card => {
        const name = card.querySelector('.pos-name')?.textContent.trim();
        const activation = card.querySelector('.activation-value')?.textContent.trim();
        lines.push(`    [${name}]  activation: ${activation}`);
        card.querySelectorAll('.pos-field').forEach(field => {
          const label = field.querySelector('.pos-field-label')?.textContent.trim();
          const value = field.querySelector('.pos-field-value')?.textContent.trim();
          lines.push(`      ${label}: ${value}`);
        });
      });
      lines.push('');
    });

    const judgeText = turn.querySelector('.verdict-text')?.textContent.trim();
    if (judgeText) lines.push(`  Judge: ${judgeText}`, '');

    const winner = turn.querySelector('.final-name')?.textContent.trim();
    const answer = turn.querySelector('.final-text')?.textContent.trim();
    if (winner && answer) lines.push(`${winner}:`, answer, '');
  });

  const date = new Date().toISOString().slice(0, 10);
  const blob = new Blob([lines.join('\n')], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `mind-simulation-${date}.txt`;
  a.click();
  URL.revokeObjectURL(url);
}

function buildLegend() {
  const legend = document.getElementById('legend');
  legend.innerHTML = Object.entries(personalityColors).map(([name, color]) =>
    `<div class="legend-item">
      <div class="legend-dot" style="background:${color}"></div>
      <span>${escHtml(name)}</span>
    </div>`
  ).join('');
}

/* ── Chat ────────────────────────────────────────────────── */
function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 160) + 'px';
  // keep highlight scroll in sync
  const hl = document.getElementById('input-highlight');
  if (hl) hl.style.height = el.style.height;
}

function syncHighlight() {
  const textarea = document.getElementById('message-input');
  const highlight = document.getElementById('input-highlight');
  if (!highlight) return;
  const raw = textarea.value;
  const html = escHtml(raw).replace(/@(\w+)/g, (match, name) => {
    const entry = Object.entries(personalityColors).find(
      ([n]) => n.toLowerCase() === name.toLowerCase()
    );
    const color = entry?.[1];
    return color
      ? `<span class="hl-mention" style="color:${color}">${match}</span>`
      : match;
  });
  highlight.innerHTML = html || '';
  highlight.scrollTop = textarea.scrollTop;
}

function insertMention(name) {
  if (isStreaming) return;
  const input = document.getElementById('message-input');
  const pos = input.selectionStart ?? input.value.length;
  const mention = `@${name} `;
  input.value = input.value.slice(0, pos) + mention + input.value.slice(pos);
  const newPos = pos + mention.length;
  input.setSelectionRange(newPos, newPos);
  input.focus();
  syncHighlight();
  autoResize(input);
}

async function sendMessage() {
  if (isStreaming || !sessionId) return;
  const input = document.getElementById('message-input');
  const message = input.value.trim();
  if (!message) return;

  input.value = '';
  input.style.height = 'auto';
  syncHighlight();
  setStreaming(true);

  const turn = createTurn(message);
  document.getElementById('messages').appendChild(turn);
  scrollToBottom();

  try {
    const res = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, message }),
    });

    if (!res.ok) {
      const err = await res.json();
      appendError(turn, err.detail || 'Request failed.');
      setStreaming(false);
      return;
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop();
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try { handleEvent(JSON.parse(line.slice(6)), turn); } catch {}
        }
      }
    }
    setStreaming(false);  // safety net if stream closes without a 'done' event
  } catch {
    appendError(turn, 'Connection lost.');
    setStreaming(false);
  }
}

function handleEvent(event, turn) {
  const debateContent = turn.querySelector('.debate-content');
  const thinkingEl = turn.querySelector('.thinking');

  switch (event.type) {
    case 'round':
      if (thinkingEl) thinkingEl.remove();
      appendRound(debateContent, event.round_num, event.positions);
      scrollToBottom();
      break;
    case 'verdict':
      appendVerdict(debateContent, event);
      scrollToBottom();
      break;
    case 'final':
      appendFinalAnswer(turn, event.winner, event.answer);
      scrollToBottom();
      break;
    case 'direct':
      turn.querySelector('.debate-block')?.remove();
      appendFinalAnswer(turn, event.winner, event.answer);
      scrollToBottom();
      break;
    case 'done':
      setStreaming(false);
      break;
    case 'error':
      appendError(turn, event.message);
      setStreaming(false);
      break;
  }
}

/* ── DOM builders ────────────────────────────────────────── */
function createTurn(message) {
  const turn = document.createElement('div');
  turn.className = 'turn';
  turn.innerHTML = `
    <div class="user-bubble">${escHtml(message)}</div>
    <div class="debate-block">
      <div class="debate-block-header">
        <span class="debate-block-title">Inner Crowd</span>
        <button class="toggle-btn" onclick="toggleDebate(this)">▾ Collapse</button>
      </div>
      <div class="debate-content">
        <div class="thinking">
          <div class="thinking-dot"></div>
          <div class="thinking-dot"></div>
          <div class="thinking-dot"></div>
        </div>
      </div>
    </div>`;
  return turn;
}

function appendRound(container, roundNum, positions) {
  const round = document.createElement('div');
  round.className = 'round';
  round.innerHTML = `<div class="round-label">Round ${roundNum}</div><div class="positions"></div>`;
  const posContainer = round.querySelector('.positions');
  positions.forEach(p => posContainer.appendChild(buildPositionCard(p)));
  container.appendChild(round);
}

function buildPositionCard(p) {
  const color = personalityColors[p.name] || 'var(--text-3)';
  const pct = Math.round(p.activation * 100);
  const card = document.createElement('div');
  card.className = 'position-card';
  card.style.setProperty('--p-color', color);
  card.innerHTML = `
    <div class="pos-header">
      <span class="pos-name" style="color:${color}" onclick="insertMention('${escHtml(p.name)}')" title="Talk to ${escHtml(p.name)} directly">${escHtml(p.name)}</span>
      <div class="activation-track">
        <div class="activation-fill" style="width:${pct}%; background:${color}"></div>
      </div>
      <span class="activation-value">${p.activation.toFixed(2)}</span>
    </div>
    <div class="pos-fields">
      <div class="pos-field"><span class="pos-field-label">to others</span><span class="pos-field-value">${escHtml(p.says_to_others)}</span></div>
      <div class="pos-field"><span class="pos-field-label">feels</span><span class="pos-field-value">${escHtml(p.inner_feeling)}</span></div>
      <div class="pos-field"><span class="pos-field-label">would say</span><span class="pos-field-value">${escHtml(p.proposed_answer)}</span></div>
    </div>`;
  return card;
}

function appendVerdict(container, verdict) {
  const el = document.createElement('div');
  el.className = 'verdict-block';
  el.innerHTML = `<span class="verdict-label">Judge</span><span class="verdict-text">${escHtml(verdict.reason)}</span>`;
  container.appendChild(el);
}

function appendFinalAnswer(turn, winner, answer) {
  const color = personalityColors[winner] || 'var(--accent)';
  const el = document.createElement('div');
  el.className = 'final-answer';
  el.style.setProperty('--p-color', color);
  el.innerHTML = `
    <div class="final-header">
      <div class="final-name">${escHtml(winner || 'Response')}</div>
      ${winner ? `<button class="reply-btn" onclick="insertMention('${escHtml(winner)}')" title="Reply to ${escHtml(winner)}">↩ Reply</button>` : ''}
    </div>
    <div class="final-text">${escHtml(answer)}</div>`;
  turn.appendChild(el);
}

function appendError(turn, message) {
  const el = document.createElement('div');
  el.className = 'error-bubble';
  el.textContent = message;
  turn.appendChild(el);
}

function toggleDebate(btn) {
  const content = btn.closest('.debate-block').querySelector('.debate-content');
  const collapsed = content.classList.toggle('collapsed');
  btn.textContent = collapsed ? '▸ Expand' : '▾ Collapse';
}

/* ── Helpers ─────────────────────────────────────────────── */
function setStreaming(val) {
  isStreaming = val;
  document.getElementById('send-btn').disabled = val;
  document.getElementById('message-input').disabled = val;
  const brain = document.getElementById('streaming-brain');
  if (brain) brain.classList.toggle('hidden', !val);
  if (!val) scrollToBottom();
}

function setLoading(val) {
  const btn = document.getElementById('start-btn');
  btn.disabled = val;
  if (val) btn.textContent = 'Starting…';
  else if (!sessionId) btn.textContent = 'Begin session';
}

function scrollToBottom() {
  const el = document.getElementById('messages');
  el.scrollTop = el.scrollHeight;
}

function escHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
