import { toggleCompare } from "./compare.js";

/**
 * Handles clicks on "Compare" buttons in list/detail pages.
 * - Prevents navigation to detail when button is inside a card <a>.
 * - Calls toggleCompare(id) to add/remove Pokémon to the compare list.
 * - Updates button CSS state (is-active).
 */
document.addEventListener("click", (e) => {
  const btn = e.target.closest(".js-cmp");
  if (!btn) return;

  e.preventDefault();
  e.stopPropagation();

  const id = btn.dataset.id;
  if (!id) return;

  toggleCompare(id).then((res) => {
    if (res?.action === "added") {
      btn.classList.add("is-active");
    } else if (res?.action === "removed") {
      btn.classList.remove("is-active");
    }
  });
});