// static/js/likes.js

function getCsrf() {
  const m = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
  return m ? decodeURIComponent(m[1]) : "";
}

async function toggleLike(url) {
  const headers = { "X-Requested-With": "XMLHttpRequest", "X-CSRFToken": getCsrf() };
  const resp = await fetch(url, { method: "POST", headers });
  let data = null;
  try { data = await resp.json(); } catch (_) {}
  if (!resp.ok || !data?.ok) throw new Error("like_failed");
  return data; // { ok: true, action: "liked"|"unliked", likes: <int> }
}

function onLikeClick(e) {
  const btn = e.target.closest(".js-like");
  if (!btn) return;

  e.preventDefault();
  e.stopPropagation();

  const url = btn.getAttribute("data-like-url");
  if (!url) return;

  toggleLike(url).then((res) => {
    const cntEl = btn.querySelector(".cnt");
    if (res.action === "liked") btn.classList.add("is-active");
    if (res.action === "unliked") btn.classList.remove("is-active");
    if (cntEl && typeof res.likes === "number") cntEl.textContent = String(res.likes);
  }).catch(() => {
    // nechtiacne chyby ignoruj (alebo zobraz toast)
  });
}

document.addEventListener("click", onLikeClick);