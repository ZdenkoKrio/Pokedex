/**
 * Team detail page:
 * - Builds a radar chart comparing team members over the chosen base stat keys.
 * - Expects JSON payloads in <script id="team-members"> and <script id="team-stats-keys">.
 */
function readJson(id, fallback) {
  try {
    const el = document.getElementById(id);
    return el ? JSON.parse(el.textContent || "null") : fallback;
  } catch (e) {
    return fallback;
  }
}

(function initChart() {
  // Load data embedded by template
  const items = readJson("team-members", []);
  const keys  = readJson("team-stats-keys", []);

  if (!Array.isArray(items) || !items.length || !Array.isArray(keys) || !keys.length) return;

  const el = document.getElementById("teamChart");
  if (!el) return;

  const ctx = el.getContext("2d");

  // Normalize datasets for Chart.js radar
  const datasets = items.map((it) => ({
    label: `#${it.id} ${it.name}`,
    data: keys.map(k => (it.stats?.[k] ?? 0)),
    fill: true,
  }));

  // eslint-disable-next-line no-undef
  new Chart(ctx, {
    type: "radar",
    data: {
      labels: keys.map(k => k.toUpperCase()),
      datasets,
    },
    options: {
      responsive: true,
      elements: { line: { borderWidth: 2 } },
      scales: { r: { beginAtZero: true } },
      plugins: { legend: { position: "top" } },
    }
  });
})();