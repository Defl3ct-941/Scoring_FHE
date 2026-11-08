const state = {
  exercises: [],
  currentId: null,
  currentDirty: false,
};

const el = (sel, root = document) => root.querySelector(sel);
const els = (sel, root = document) => Array.from(root.querySelectorAll(sel));

function escapeHtml(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// ---------------------------------------------------------------
// Mini-markdown -> HTML (headers, bold, code, listes, blocs de code)
// ---------------------------------------------------------------
function inlineMd(text) {
  text = escapeHtml(text);
  text = text.replace(/`([^`]+)`/g, "<code>$1</code>");
  text = text.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  return text;
}

function mdToHtml(md) {
  const lines = md.split("\n");
  let html = "";
  let i = 0;
  let listBuffer = null; // { type: 'ul'|'ol', items: [] }

  function flushList() {
    if (!listBuffer) return;
    const tag = listBuffer.type;
    html += `<${tag}>` + listBuffer.items.map((it) => `<li>${inlineMd(it)}</li>`).join("") + `</${tag}>`;
    listBuffer = null;
  }

  while (i < lines.length) {
    const line = lines[i];

    if (line.startsWith("```")) {
      const codeLines = [];
      i++;
      while (i < lines.length && !lines[i].startsWith("```")) {
        codeLines.push(lines[i]);
        i++;
      }
      flushList();
      html += `<pre><code>${escapeHtml(codeLines.join("\n"))}</code></pre>`;
      i++;
      continue;
    }

    if (/^#{1,3}\s/.test(line)) {
      flushList();
      const level = line.match(/^#+/)[0].length;
      html += `<h${level}>${inlineMd(line.replace(/^#+\s*/, ""))}</h${level}>`;
      i++;
      continue;
    }

    if (/^---+$/.test(line.trim())) {
      flushList();
      i++;
      continue;
    }

    const ulMatch = line.match(/^\s*-\s+(.*)/);
    const olMatch = line.match(/^\s*\d+\.\s+(.*)/);
    if (ulMatch) {
      if (!listBuffer || listBuffer.type !== "ul") { flushList(); listBuffer = { type: "ul", items: [] }; }
      listBuffer.items.push(ulMatch[1]);
      i++;
      continue;
    }
    if (olMatch) {
      if (!listBuffer || listBuffer.type !== "ol") { flushList(); listBuffer = { type: "ol", items: [] }; }
      listBuffer.items.push(olMatch[1]);
      i++;
      continue;
    }

    flushList();
    if (line.trim() === "") { i++; continue; }
    html += `<p>${inlineMd(line)}</p>`;
    i++;
  }
  flushList();
  return html;
}

// ---------------------------------------------------------------
// Chargement des exercices
// ---------------------------------------------------------------
async function loadExercises() {
  const res = await fetch("/api/exercises");
  const data = await res.json();
  state.exercises = data.exercises;
  renderSidebar();
  renderGlobalProgress();
}

function renderGlobalProgress() {
  const total = state.exercises.length;
  const passed = state.exercises.filter((e) => e.passed).length;
  const pct = total ? (passed / total) * 100 : 0;
  el("#globalProgressFill").style.width = `${pct}%`;
  el("#globalProgressLabel").textContent = `${passed} / ${total} exercices réussis`;
}

function renderSidebar() {
  const container = el("#exerciseList");
  container.innerHTML = "";
  let lastModule = null;

  state.exercises.forEach((ex) => {
    if (ex.module !== lastModule) {
      const h = document.createElement("div");
      h.className = "module-heading";
      h.textContent = ex.module;
      container.appendChild(h);
      lastModule = ex.module;
    }

    const item = document.createElement("div");
    item.className = "ex-item" + (ex.locked ? " locked" : "") + (ex.id === state.currentId ? " active" : "");
    const icon = ex.passed ? "✅" : ex.locked ? "🔒" : "⬜";
    item.innerHTML = `
      <span class="ex-icon">${icon}</span>
      <div>
        <div class="ex-item-title">${ex.order}. ${ex.title}</div>
        <div class="ex-item-sub">${ex.difficulty}${ex.bonus ? " · bonus" : ""}</div>
      </div>
    `;
    item.addEventListener("click", () => {
      if (ex.locked) {
        alert(`Verrouillé. Terminez d'abord : ${ex.missing_dependencies.join(", ")}`);
        return;
      }
      selectExercise(ex.id);
    });
    container.appendChild(item);
  });
}

// ---------------------------------------------------------------
// Sélection + affichage d'un exercice
// ---------------------------------------------------------------
async function selectExercise(id) {
  state.currentId = id;
  renderSidebar();

  const res = await fetch(`/api/exercises/${id}`);
  const ex = await res.json();
  renderExercisePanel(ex);
}

function renderExercisePanel(ex) {
  const content = el("#content");
  content.innerHTML = `
    <div class="exercise-panel">
      <div class="exercise-header">
        <h2 class="exercise-title">${ex.order}. ${ex.title}</h2>
        <div class="exercise-badges">
          <span class="badge neutral">${ex.difficulty}</span>
          ${ex.bonus ? '<span class="badge info">bonus</span>' : ""}
          ${ex.progress.passed ? '<span class="badge ok">réussi ✓</span>' : '<span class="badge no">pas encore réussi</span>'}
        </div>
      </div>

      <div class="statement">${mdToHtml(ex.statement)}</div>

      <div class="editor-section">
        <div class="editor-toolbar">
          <h3>Votre code : exercise.py</h3>
          <div class="editor-actions">
            <button class="btn subtle" id="reloadBtn" title="Recharge la dernière version enregistrée sur le serveur">↺ Recharger</button>
            <button class="btn danger-ghost" id="restartExerciseBtn" title="Remet le code de départ et efface votre progression sur cet exercice">🗑️ Réinitialiser l'exercice</button>
            <button class="btn ghost" id="saveBtn">💾 Enregistrer</button>
            <button class="btn primary" id="runBtn">▶ Lancer les tests</button>
          </div>
        </div>
        <textarea class="code-editor" id="codeEditor" spellcheck="false">${escapeHtml(ex.code)}</textarea>
      </div>

      <div class="result-banner" id="resultBanner"></div>
      <pre class="console" id="consoleOutput"></pre>

      <div class="solution-block">
        <div class="solution-toggle" id="solutionToggle">👁️ Afficher la solution de référence</div>
        <div class="solution-code" id="solutionCode"></div>
      </div>
    </div>
  `;

  el("#saveBtn").addEventListener("click", () => saveCode(ex.id));
  el("#runBtn").addEventListener("click", () => runTests(ex.id));
  el("#reloadBtn").addEventListener("click", () => selectExercise(ex.id));
  el("#restartExerciseBtn").addEventListener("click", () => resetExercise(ex.id));
  el("#solutionToggle").addEventListener("click", () => toggleSolution(ex.id));
}

async function resetExercise(id) {
  const confirmed = confirm(
    "Réinitialiser cet exercice ?\n\nVotre code sera remplacé par le stub de départ et votre progression (réussi / tentatives) sur CET exercice sera effacée. Cette action est irréversible."
  );
  if (!confirmed) return;

  const btn = el("#restartExerciseBtn");
  btn.disabled = true;
  const original = btn.textContent;
  btn.textContent = "Réinitialisation…";

  try {
    const res = await fetch(`/api/exercises/${id}/reset`, { method: "POST" });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      alert("Erreur lors de la réinitialisation : " + (err.detail || res.status));
      return;
    }
    await loadExercises();
    await selectExercise(id);
  } finally {
    if (btn.isConnected) {
      btn.disabled = false;
      btn.textContent = original;
    }
  }
}

async function resetAll() {
  const confirmed = confirm(
    "Tout réinitialiser ?\n\nLes 10 exercices seront remis à leur code de départ et TOUTE la progression sera effacée. Cette action est irréversible."
  );
  if (!confirmed) return;

  const btn = el("#resetAllBtn");
  btn.disabled = true;
  const original = btn.textContent;
  btn.textContent = "Réinitialisation…";

  try {
    const res = await fetch(`/api/reset-all`, { method: "POST" });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      alert("Erreur lors de la réinitialisation : " + (err.detail || res.status));
      return;
    }
    await loadExercises();
    if (state.currentId) {
      await selectExercise(state.currentId);
    }
  } finally {
    btn.disabled = false;
    btn.textContent = original;
  }
}

el("#resetAllBtn").addEventListener("click", resetAll);

async function saveCode(id, { silent = false } = {}) {
  const code = el("#codeEditor").value;
  const res = await fetch(`/api/exercises/${id}/save`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    alert("Erreur lors de l'enregistrement : " + (err.detail || res.status));
    return false;
  }
  if (!silent) {
    const btn = el("#saveBtn");
    const original = btn.textContent;
    btn.textContent = "✓ Enregistré";
    setTimeout(() => (btn.textContent = original), 1200);
  }
  return true;
}

async function runTests(id) {
  const runBtn = el("#runBtn");
  const banner = el("#resultBanner");
  const consoleEl = el("#consoleOutput");

  const saved = await saveCode(id, { silent: true });
  if (!saved) return;

  const original = runBtn.textContent;
  runBtn.disabled = true;
  runBtn.innerHTML = `<span class="loader"></span> Exécution des tests…`;
  banner.className = "result-banner";
  consoleEl.className = "console";

  try {
    const res = await fetch(`/api/exercises/${id}/run`, { method: "POST" });
    const data = await res.json();

    consoleEl.textContent = data.output;
    consoleEl.classList.add("show");

    banner.classList.add("show");
    if (data.timed_out) {
      banner.classList.add("timeout");
      banner.textContent = `⏱️ Délai dépassé (${data.summary})`;
    } else if (data.passed) {
      banner.classList.add("pass");
      banner.textContent = `✅ Tous les tests passent (${data.summary})`;
    } else {
      banner.classList.add("fail");
      banner.textContent = `❌ Des tests échouent (${data.summary})`;
    }

    // rafraîchit la sidebar (progression, déverrouillage éventuel)
    await loadExercises();
    renderSidebar();
  } catch (err) {
    banner.classList.add("show", "fail");
    banner.textContent = "Erreur réseau lors de l'exécution des tests.";
    console.error(err);
  } finally {
    runBtn.disabled = false;
    runBtn.textContent = original;
  }
}

async function toggleSolution(id) {
  const box = el("#solutionCode");
  const toggle = el("#solutionToggle");
  if (box.classList.contains("show")) {
    box.classList.remove("show");
    toggle.textContent = "👁️ Afficher la solution de référence";
    return;
  }
  if (!confirm("Essayez vraiment de résoudre l'exercice par vous-même d'abord. Afficher la solution ?")) {
    return;
  }
  const res = await fetch(`/api/exercises/${id}/solution`);
  if (!res.ok) {
    box.innerHTML = "<p>Pas de solution disponible pour cet exercice.</p>";
  } else {
    const data = await res.json();
    box.innerHTML = `<pre><code>${escapeHtml(data.solution)}</code></pre>`;
  }
  box.classList.add("show");
  toggle.textContent = "🙈 Masquer la solution";
}

loadExercises();
