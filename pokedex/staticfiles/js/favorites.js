/**
 * Toggle Pokémon in user's favorites.
 * POST -> /favorites/toggle/<id>/ ; expects CSRF cookie "csrftoken"
 */
export async function toggleFavorite(pokeId) {
  const url = `/favorites/toggle/${pokeId}/`;
  const headers = { "X-Requested-With": "XMLHttpRequest" };

  const m = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
  if (m) headers["X-CSRFToken"] = decodeURIComponent(m[1]);

  const resp = await fetch(url, { method: "POST", headers });
  let data = null;
  try { data = await resp.json(); } catch (_) {}

  if (!resp.ok) return { ok: false, ...(data || {}) };
  return { ok: true, ...(data || {}) };
}