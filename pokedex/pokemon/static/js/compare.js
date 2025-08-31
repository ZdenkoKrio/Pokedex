/**
 * Toggle Pokémon in the comparison list (session-based).
 *
 * Sends a POST request to Django endpoint (`compare_toggle`).
 * - Extracts CSRF token from cookies (Django default: `csrftoken`).
 * - Returns a JSON object with `ok`, `action`, `count`, etc.
 *
 * @param {string} toggleUrl - The URL of the toggle endpoint.
 * @returns {Promise<object>} - Normalized response from server.
 */

export async function toggleCompare(toggleUrl) {
  const headers = { "X-Requested-With": "XMLHttpRequest" };

  // CSRF token from cookie
  const m = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
  if (m) headers["X-CSRFToken"] = decodeURIComponent(m[1]);

  const resp = await fetch(toggleUrl, {
    method: "POST",
    headers,
  });

  let data = null;
  try { data = await resp.json(); } catch (_) {}

  if (!resp.ok) {
    return { ok: false, ...(data || {}) };
  }
  return { ok: true, ...(data || {}) };
}