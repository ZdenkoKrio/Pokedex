/**
 * Compare page logic (compare.html).
 *
 * Features:
 *  - Toggle buttons: adds/removes Pokémon from comparison and reloads the page.
 *  - Radar chart: built with Chart.js from template-provided JSON.
 *  - Client-side sorting of table rows by ID/Name/BST or any STAT (ASC/DESC).
 *    Also reorders the radar chart datasets to match the table order.
 */

import { toggleCompare } from "./compare.js";

let chartInstance = null;
let items = [];
let keys = [];

/* ---------- Toggles ---------- */
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
        window.location.reload(); // refresh: table + chart
      }
    });
  });
}

/* ---------- Chart ---------- */
function buildRadar(orderIds = null) {
  // Chart data is loaded once globally
  if (!items.length || !keys.length) return;

  const el = document.getElementById("cmpChart");
  if (!el) return;

  const ctx = el.getContext("2d");

  const order = Array.isArray(orderIds) && orderIds.length
    ? orderIds
    : items.map((it) => it.id);

  const datasets = order.map((id) => {
    const it = items.find((x) => x.id === id);
    return {
      label: `#${it.id} ${it.name}`,
      data: keys.map((k) => (it.stats?.[k] ?? 0)),
      fill: true,
    };
  });

  // Destroy previous chart if present
  if (chartInstance) {
    chartInstance.destroy();
  }

  // eslint-disable-next-line no-undef
  chartInstance = new Chart(ctx, {
    type: "radar",
    data: { labels: keys.map((k) => k.toUpperCase()), datasets },
    options: {
      responsive: true,
      elements: { line: { borderWidth: 2 } },
      scales: { r: { beginAtZero: true } },
      plugins: { legend: { position: "top" } },
    },
  });
}

/* ---------- Sorting ---------- */
function readTemplateJSON() {
  const itemsJson = document.getElementById("cmp-data")?.textContent || "[]";
  const keysJson = document.getElementById("cmp-keys")?.textContent || "[]";
  try { items = JSON.parse(itemsJson); } catch (_) { items = []; }
  try { keys = JSON.parse(keysJson); } catch (_) { keys = []; }
}

function computeSum(it) {
  return keys.reduce((acc, k) => acc + (Number(it.stats?.[k] ?? 0) || 0), 0);
}

function getMetricValue(it, metric) {
  if (metric === "id") return Number(it.id);
  if (metric === "name") return String(it.name).toLowerCase();
  if (metric === "sum") return computeSum(it);
  // stat
  return Number(it.stats?.[metric] ?? 0);
}

function applySort() {
  const sortSel = document.getElementById("cmp-sort");
  const dirSel = document.getElementById("cmp-dir");
  const metric = sortSel?.value || "id";
  const dir = dirSel?.value === "asc" ? 1 : -1;

  const tbody = document.querySelector("#cmp-table tbody");
  if (!tbody) return;

  // current order of <tr> by id
  const rows = Array.from(tbody.querySelectorAll("tr[data-id]"));
  if (!rows.length) return;

  // build comparator using items JSON
  const cmp = (a, b) => {
    const ida = Number(a.dataset.id);
    const idb = Number(b.dataset.id);
    const ia = items.find((x) => x.id === ida);
    const ib = items.find((x) => x.id === idb);
    const va = getMetricValue(ia, metric);
    const vb = getMetricValue(ib, metric);

    if (typeof va === "string" && typeof vb === "string") {
      return dir * va.localeCompare(vb);
    }
    return dir * ((va > vb) - (va < vb));
  };

  rows.sort(cmp).forEach((tr) => tbody.appendChild(tr));

  // also reorder chart datasets to match the new row order
  const orderIds = rows.map((r) => Number(r.dataset.id));
  buildRadar(orderIds);
}

function bindSort() {
  const btn = document.getElementById("cmp-apply");
  const sortSel = document.getElementById("cmp-sort");
  const dirSel = document.getElementById("cmp-dir");

  const trigger = () => applySort();

  btn?.addEventListener("click", trigger);
  sortSel?.addEventListener("change", trigger);
  dirSel?.addEventListener("change", trigger);
}

/* ---------- Init ---------- */
readTemplateJSON();
bindToggles();
bindSort();
buildRadar();