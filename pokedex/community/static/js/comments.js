function getCsrf() {
  const m = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
  return m ? decodeURIComponent(m[1]) : "";
}

async function postComment(url, body) {
  const headers = {
    "X-Requested-With": "XMLHttpRequest",
    "X-CSRFToken": getCsrf(),
    "Content-Type": "application/x-www-form-urlencoded",
  };
  const resp = await fetch(url, { method: "POST", headers, body: new URLSearchParams({ body }) });
  const data = await resp.json().catch(() => ({}));
  if (!resp.ok || !data?.ok) throw new Error(data?.error || "comment_failed");
  return data.comment;
}

async function deleteComment(url) {
  const headers = { "X-Requested-With": "XMLHttpRequest", "X-CSRFToken": getCsrf() };
  const resp = await fetch(url, { method: "POST", headers });
  const data = await resp.json().catch(() => ({}));
  if (!resp.ok || !data?.ok) throw new Error(data?.error || "delete_failed");
  return true;
}

function onSubmit(e) {
  const form = e.target.closest("#comment-form");
  if (!form) return;
  e.preventDefault();

  const url = form.getAttribute("data-post-url");
  const textarea = form.querySelector("#comment-body");
  const val = (textarea?.value || "").trim();
  if (!url || !val) return;

  postComment(url, val).then((c) => {
    textarea.value = "";
    const list = document.getElementById("comment-list");
    const li = document.createElement("li");
    li.setAttribute("data-id", String(c.id));
    li.innerHTML = `
      <div class="c-head">
        <a href="/community/users/${c.author_id}/">@${c.author}</a>
        <span class="when">just now</span>
        ${c.can_delete ? `<button class="c-del js-del" data-del-url="/community/comments/${c.id}/delete/">Delete</button>` : ""}
      </div>
      <div class="c-body"></div>
    `;
    li.querySelector(".c-body").textContent = c.body;
    // remove "No comments yet." placeholder if present
    const empty = list.querySelector(".empty");
    if (empty) empty.remove();
    list.prepend(li);
  }).catch(() => {});
}

function onDelete(e) {
  const btn = e.target.closest(".js-del");
  if (!btn) return;
  e.preventDefault();
  const url = btn.getAttribute("data-del-url");
  if (!url) return;

  deleteComment(url).then(() => {
    const card = btn.closest("li");
    if (card) card.remove();
  }).catch(() => {});
}

document.addEventListener("submit", onSubmit);
document.addEventListener("click", onDelete);