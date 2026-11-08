const state = {
  model: null,
  values: {},
};

const el = (sel) => document.querySelector(sel);
const els = (sel) => Array.from(document.querySelectorAll(sel));

function fmt(n, digits = 2) {
  return Number(n).toLocaleString("fr-FR", { maximumFractionDigits: digits, minimumFractionDigits: 0 });
}

function fmtBytes(n) {
  if (n < 1024) return `${n} o`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} Ko`;
  return `${(n / (1024 * 1024)).toFixed(2)} Mo`;
}

// ---------------------------------------------------------------
// Navigation entre étapes
// ---------------------------------------------------------------
function goToStep(step) {
  els(".step-btn").forEach((b) => b.classList.toggle("active", b.dataset.step === String(step)));
  els(".panel").forEach((p) => p.classList.toggle("active", p.dataset.panel === String(step)));
  window.scrollTo({ top: 0, behavior: "smooth" });
}

document.addEventListener("click", (e) => {
  const stepBtn = e.target.closest(".step-btn");
  if (stepBtn) goToStep(stepBtn.dataset.step);
  const gotoBtn = e.target.closest("[data-goto]");
  if (gotoBtn) goToStep(gotoBtn.dataset.goto);
});

// ---------------------------------------------------------------
// Sliders (données client) + score en clair calculé en direct
// ---------------------------------------------------------------
function renderSliders() {
  const container = el("#sliders");
  container.innerHTML = "";
  state.model.features.forEach((f) => {
    state.values[f.key] = f.default;
    const row = document.createElement("div");
    row.className = "slider-row";
    row.innerHTML = `
      <label>
        <span>${f.label}</span>
        <span class="val" id="val-${f.key}">${f.default}${f.unit ? " " + f.unit : ""}</span>
      </label>
      <input type="range" id="slider-${f.key}" min="${f.min}" max="${f.max}" step="${f.step}" value="${f.default}" />
      <div class="feature-help">${f.help}</div>
    `;
    container.appendChild(row);
  });

  state.model.features.forEach((f) => {
    el(`#slider-${f.key}`).addEventListener("input", (e) => {
      const v = Number(e.target.value);
      state.values[f.key] = v;
      el(`#val-${f.key}`).textContent = `${v}${f.unit ? " " + f.unit : ""}`;
      updatePlaintextScore();
    });
  });
}

function computePlaintextScore() {
  const { revenu, ratio_endettement, incidents } = state.values;
  const [wRevenu, wRatio, wIncidents] = state.model.weights;
  return (
    state.model.bias +
    wRevenu * (revenu - 2500) +
    wRatio * ratio_endettement +
    wIncidents * incidents
  );
}

function updatePlaintextScore() {
  const score = computePlaintextScore();
  el("#plaintextScore").textContent = fmt(score, 2);
  const [wRevenu, wRatio, wIncidents] = state.model.weights;
  el("#plaintextFormula").textContent =
    `${state.model.bias} + ${wRevenu}·(${state.values.revenu}-2500) + ${wRatio}·${state.values.ratio_endettement} + ${wIncidents}·${state.values.incidents} = ${fmt(score, 2)}`;
}

// ---------------------------------------------------------------
// Appels API
// ---------------------------------------------------------------
async function postScoring(path) {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(state.values),
  });
  if (!res.ok) throw new Error(`Erreur API ${path}: ${res.status}`);
  return res.json();
}

async function withLoading(button, fn) {
  const original = button.textContent;
  button.disabled = true;
  button.innerHTML = `<span class="loader"></span> Calcul en cours…`;
  try {
    await fn();
  } catch (err) {
    console.error(err);
    alert("Une erreur est survenue : " + err.message);
  } finally {
    button.disabled = false;
    button.textContent = original;
  }
}

// ---------------------------------------------------------------
// Étape 1 : Classique
// ---------------------------------------------------------------
el("#runClassic").addEventListener("click", (e) =>
  withLoading(e.target, async () => {
    const data = await postScoring("/api/step/classic");
    renderClassic(data);
  })
);

function renderClassic(data) {
  const area = el("#classicResult");
  area.innerHTML = `
    <div class="trace-grid">
      <div class="trace-card">
        <h4>Vos 3 valeurs, une fois chiffrées</h4>
        ${data.ciphertext_previews.map((c) => `<div class="mono">${c}</div>`).join("")}
      </div>
      <div class="trace-card">
        <h4>Tentative du serveur</h4>
        <p style="font-size:13px">${data.server_attempt.description}</p>
        <div class="mono">${data.server_attempt.forged_preview ?? "(aucun aperçu)"}</div>
        <p style="font-size:13px;margin-top:8px;color:var(--warning)">${data.server_attempt.result}
          <span class="badge no">calcul impossible</span>
        </p>
      </div>
      <div class="trace-card">
        <h4>Métriques</h4>
        <div>Taille totale chiffrée : <strong>${fmtBytes(data.total_ciphertext_bytes)}</strong></div>
        <div>Temps de chiffrement : <strong>${data.timings_ms.encryption} ms</strong></div>
      </div>
    </div>
  `;
  const c = el("#classicConclusion");
  c.hidden = false;
  c.textContent = data.conclusion;
}

// ---------------------------------------------------------------
// Étape 2 : Paillier
// ---------------------------------------------------------------
el("#runPaillier").addEventListener("click", (e) =>
  withLoading(e.target, async () => {
    const data = await postScoring("/api/step/paillier");
    renderPaillier(data);
  })
);

function renderPaillier(data) {
  const area = el("#paillierResult");
  const match = data.exact_match;
  area.innerHTML = `
    <div class="trace-grid">
      <div class="trace-card">
        <h4>Clé publique Paillier</h4>
        <div>Taille de n : <strong>${data.public_key_preview.n_bits} bits</strong></div>
        <div class="mono">n = ${data.public_key_preview.n_preview}</div>
      </div>
      <div class="trace-card">
        <h4>Vos 3 valeurs chiffrées E(x_i)</h4>
        ${data.ciphertext_previews.map((c) => `<div class="mono">${c}</div>`).join("")}
      </div>
      <div class="trace-card">
        <h4>Calcul homomorphe côté serveur</h4>
        <p style="font-size:13px">${data.server_computation.description}</p>
        <div class="mono">${data.server_computation.final_ciphertext_preview}</div>
      </div>
      <div class="trace-card">
        <h4>Résultat déchiffré (client)</h4>
        <div class="big">${fmt(data.decrypted_result, 2)}</div>
        <div style="font-size:12.5px;color:var(--text-muted)">
          Référence en clair : ${fmt(data.plaintext_reference, 2)}
          <span class="badge ${match ? "ok" : "no"}">${match ? "identique ✓" : "différent"}</span>
        </div>
      </div>
      <div class="trace-card">
        <h4>Temps (ms)</h4>
        <div>Chiffrement client : <strong>${data.timings_ms.client_encryption}</strong></div>
        <div>Calcul serveur : <strong>${data.timings_ms.server_homomorphic_computation}</strong></div>
        <div>Déchiffrement client : <strong>${data.timings_ms.client_decryption}</strong></div>
      </div>
    </div>
  `;
  const c = el("#paillierConclusion");
  c.hidden = false;
  c.textContent = data.conclusion;
}

// ---------------------------------------------------------------
// Étape 3 : CKKS / FHE
// ---------------------------------------------------------------
el("#runCkks").addEventListener("click", (e) =>
  withLoading(e.target, async () => {
    const data = await postScoring("/api/step/ckks");
    renderCkks(data);
  })
);

function renderCkks(data) {
  const area = el("#ckksResult");
  area.innerHTML = `
    <div class="trace-grid">
      <div class="trace-card">
        <h4>Paramètres CKKS</h4>
        <div>poly_modulus_degree : <strong>${data.params.poly_modulus_degree}</strong></div>
        <div>coeff_mod_bit_sizes : <strong>${data.params.coeff_mod_bit_sizes.join(", ")}</strong></div>
      </div>
      <div class="trace-card">
        <h4>Expansion des données</h4>
        <div>Vecteur en clair : <strong>${fmtBytes(data.sizes_bytes.plaintext_vector)}</strong></div>
        <div>Vecteur chiffré : <strong>${fmtBytes(data.sizes_bytes.ciphertext_vector)}</strong></div>
        <div>Facteur d'expansion : <strong>×${fmt(data.expansion_ratio, 1)}</strong></div>
      </div>
      <div class="trace-card">
        <h4>Tentative de déchiffrement... côté serveur</h4>
        <p style="font-size:13px;color:var(--warning)">${data.server_attempt_to_decrypt}
          <span class="badge no">bloqué</span>
        </p>
      </div>
      <div class="trace-card">
        <h4>Résultat déchiffré (client, seul détenteur de la clé)</h4>
        <div class="big">${fmt(data.decrypted_result, 4)}</div>
        <div style="font-size:12.5px;color:var(--text-muted)">
          Référence en clair : ${fmt(data.plaintext_reference, 4)}, erreur absolue : ${data.absolute_error.toExponential(2)}
          <span class="badge ok">approximation ✓</span>
        </div>
      </div>
      <div class="trace-card">
        <h4>Temps (ms)</h4>
        ${Object.entries(data.timings_ms).map(([k, v]) => `<div>${k.replace(/_/g, " ")} : <strong>${v}</strong></div>`).join("")}
      </div>
    </div>
  `;
  const c = el("#ckksConclusion");
  c.hidden = false;
  c.textContent = data.conclusion;
}

// ---------------------------------------------------------------
// Étape 4 : Comparatif
// ---------------------------------------------------------------
el("#runCompare").addEventListener("click", (e) =>
  withLoading(e.target, async () => {
    const data = await postScoring("/api/compare");
    renderCompare(data);
  })
);

function barChart(rows, maxKey, unitFmt) {
  const max = Math.max(...rows.map((r) => r.value)) || 1;
  const colors = { Classique: "#b5560a", "Paillier (PHE)": "#0f8a5f", "FHE (CKKS)": "#4f46e5" };
  return `<div class="chart">${rows
    .map(
      (r) => `
      <div class="chart-row">
        <div class="chart-label">${r.label}</div>
        <div class="chart-track"><div class="chart-fill" style="width:${(r.value / max) * 100}%; background:${colors[r.label]}"></div></div>
        <div class="chart-value">${unitFmt(r.value)}</div>
      </div>`
    )
    .join("")}</div>`;
}

function renderCompare(data) {
  const area = el("#compareResult");
  const rowsTime = [
    { label: "Classique", value: data.classic.temps_ms },
    { label: "Paillier (PHE)", value: data.paillier.temps_ms },
    { label: "FHE (CKKS)", value: data.ckks.temps_ms },
  ];
  const rowsSize = [
    { label: "Classique", value: data.classic.taille_chiffre_octets },
    { label: "Paillier (PHE)", value: data.paillier.taille_chiffre_octets },
    { label: "FHE (CKKS)", value: data.ckks.taille_chiffre_octets },
  ];

  area.innerHTML = `
    <p><strong>Score en clair de référence :</strong> ${fmt(data.plaintext_score, 4)}</p>

    <h3 style="font-size:14px;margin-top:20px;">⏱️ Temps de calcul total (ms, échelle log visuelle simplifiée)</h3>
    ${barChart(rowsTime, "temps_ms", (v) => `${fmt(v, 2)} ms`)}

    <h3 style="font-size:14px;margin-top:20px;">📦 Taille des données chiffrées</h3>
    ${barChart(rowsSize, "taille", (v) => fmtBytes(v))}

    <table class="compare-table">
      <thead>
        <tr><th>Approche</th><th>Calcul sur chiffré ?</th><th>Résultat</th><th>Précision</th><th>Opérations supportées</th></tr>
      </thead>
      <tbody>
        <tr>
          <td>Classique (AES/Fernet)</td>
          <td><span class="badge no">non</span></td>
          <td>non calculable</td>
          <td>${data.classic.precision}</td>
          <td>aucune</td>
        </tr>
        <tr>
          <td>Paillier (PHE)</td>
          <td><span class="badge ok">oui</span></td>
          <td>${fmt(data.paillier.resultat, 2)}</td>
          <td>${data.paillier.precision}</td>
          <td>${data.paillier.operations_supportees}</td>
        </tr>
        <tr>
          <td>FHE complet (CKKS)</td>
          <td><span class="badge ok">oui</span></td>
          <td>${fmt(data.ckks.resultat, 4)}</td>
          <td>${data.ckks.precision}</td>
          <td>${data.ckks.operations_supportees}</td>
        </tr>
      </tbody>
    </table>
  `;
}

// ---------------------------------------------------------------
// Init
// ---------------------------------------------------------------
async function init() {
  const res = await fetch("/api/model");
  state.model = await res.json();
  renderSliders();
  updatePlaintextScore();
}

init();
