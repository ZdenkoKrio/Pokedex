/**
 * Compare page logic (compare.html).
 *
 * Features:
 *  - Handles toggle buttons for each Pokémon.
 *    -> Sends AJAX toggle and reloads page to update table/chart.
 *  - Builds a radar chart with Chart.js from template-provided JSON.
 */

import { toggleCompare } from "./compare.js";


function bindToggles() {
  document.addEventListener("click", (e) => {
    const btn = e.target.closest(".js-cmp");
    if (!btn) return;

    e.preventDefault();
    e.stopPropagation();

    const id = btn.dataset.id;
    if (!id) return;

    toggleCompare(id).then((res) => {
      if (res?.ok) {
         window.location.reload();
      }
    });
  });
}


function buildRadar() {
  const itemsJson = document.getElementById("cmp-data")?.textContent || "[]";
  const keysJson  = document.getElementById("cmp-keys")?.textContent || "[]";

  let items = [], keys = [];
  try { items = JSON.parse(itemsJson); } catch(_){}
  try { keys  = JSON.parse(keysJson);  } catch(_){}

  if (!items.length || !keys.length) return;

  const el = document.getElementById("cmpChart");
  if (!el) return;

  const ctx = el.getContext("2d");

  const datasets = items.map((it) => ({
    label: `#${it.id} ${it.name}`,
    data: keys.map(k => (it.stats?.[k] ?? 0)),
    fill: true,
  }));

  new Chart(ctx, {
    type: "radar",
    data: { labels: keys.map(k => k.toUpperCase()), datasets },
    options: {
      responsive: true,
      elements: { line: { borderWidth: 2 } },
      scales: { r: { beginAtZero: true } },
      plugins: { legend: { position: "top" } },
    }
  });
}

bindToggles();
buildRadar();