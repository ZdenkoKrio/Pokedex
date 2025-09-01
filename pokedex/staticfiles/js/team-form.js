function readIndex() {
  try {
    const el = document.getElementById("pokemon-index");
    const items = el ? JSON.parse(el.textContent || "[]") : [];
    const byName = new Map();
    for (const it of items) {
      if (it && typeof it.name === "string") {
        byName.set(it.name.toLowerCase(), it.id);
      }
    }
    return { items, byName };
  } catch (_) {
    return { items: [], byName: new Map() };
  }
}
const { byName } = readIndex();

function setValueById(id, value) {
  const input = document.getElementById(id);
  if (input) input.value = value ?? "";
}

function getRowSlotNum(elem) {
  const row = elem.closest(".slot-grid");
  const visSlot = row?.getAttribute("data-slot-num");
  const n = Number(visSlot);
  return Number.isFinite(n) && n > 0 ? String(n) : "";
}

function setHiddenPair(elem, pokemonId) {
  const targetId = elem.getAttribute("data-target");
  const slotTargetId = elem.getAttribute("data-slot-target");
  if (!targetId || !slotTargetId) return;

  const slotVal = getRowSlotNum(elem);
  setValueById(targetId, pokemonId || "");
  if (slotVal) setValueById(slotTargetId, slotVal);
}

// --- Handlers ---------------------------------------------------------------

function onFavPick(e) {
  const sel = e.target.closest(".js-favpick");
  if (!sel) return;
  setHiddenPair(sel, sel.value || "");
}

function onSearch(e) {
  const inp = e.target.closest(".js-search");
  if (!inp) return;

  const raw = (inp.value || "").trim();
  if (!raw) {
    setHiddenPair(inp, "");
    return;
  }

  const asNum = Number(raw);
  if (!Number.isNaN(asNum) && asNum > 0) {
    setHiddenPair(inp, String(asNum));
    return;
  }

  const id = byName.get(raw.toLowerCase());
  setHiddenPair(inp, id ? String(id) : "");
}

function initialSync() {
  document.querySelectorAll(".slot-grid").forEach((row) => {
    const slotNum = row.getAttribute("data-slot-num");
    if (!slotNum) return;

    const hiddenSlot = row.querySelector('input[type="hidden"][id$="-slot"]');
    if (hiddenSlot && !hiddenSlot.value) {
      hiddenSlot.value = slotNum;
    }

    const favSel = row.querySelector(".js-favpick");
    if (favSel && favSel.value) {
      setHiddenPair(favSel, favSel.value);
      return;
    }

    const searchInp = row.querySelector(".js-search");
    if (searchInp && searchInp.value) {
      onSearch({ target: searchInp });
    }
  });
}

// --- Events -----------------------------------------------------------------

document.addEventListener("change", onFavPick);
document.addEventListener("change", onSearch);
document.addEventListener("input", onSearch);
document.addEventListener("blur", onSearch, true);

document.addEventListener("DOMContentLoaded", initialSync);