/**
 * Favorites button logic for list/detail pages AND the favorites page.
 *
 * - Handles clicks on `.js-fav` buttons.
 * - Prevents card navigation when the button sits inside a link.
 * - Calls `toggleFavorite()` and toggles `is-active` class.
 * - Updates navbar badge #fav-badge if present.
 * - If the button has data-remove="true" (favorites page), remove the card
 *   from the DOM when the item is unfavorited and show an empty state if needed.
 */
import { toggleFavorite } from "./favorites.js";

function removeCardIfNeeded(btn, res) {
  if (res.action !== "removed") return;
  if (btn.dataset.remove !== "true") return;

  const card = btn.closest(".card");
  if (card) card.remove();

  // If the grid becomes empty, show a friendly message
  const grid = document.getElementById("fav-grid");
  if (grid && grid.children.length === 0) {
    const dexUrl = grid.dataset.dexUrl || "/pokedex/";
    grid.outerHTML = `
      <p>No favorites yet. Go to the <a href="${dexUrl}">Pokédex</a> and add some!</p>
    `;
  }
}

function onFavClick(e) {
  const btn = e.target.closest(".js-fav");
  if (!btn) return;

  // Avoid navigation if inside a link/card
  e.preventDefault();
  e.stopPropagation();

  const id = btn.dataset.id;
  if (!id) return;

  toggleFavorite(id).then((res) => {
    if (!res?.ok) return;

    // Toggle visual state for generic pages
    if (res.action === "added") btn.classList.add("is-active");
    else if (res.action === "removed") btn.classList.remove("is-active");

    // Update optional badge
    const badge = document.querySelector("#fav-badge");
    if (badge && typeof res.count === "number") {
      badge.textContent = res.count;
    }

    // On favorites page: remove the card immediately when unfavorited
    removeCardIfNeeded(btn, res);
  });
}

document.addEventListener("click", onFavClick);