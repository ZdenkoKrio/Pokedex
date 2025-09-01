document.addEventListener("DOMContentLoaded", () => {
  const carousel = document.getElementById("flavorCarousel");
  if (!carousel) return;

  const slides = carousel.querySelectorAll(".flavor-slide");
  const nav = document.querySelector(".flavor-nav");
  if (!nav) return;

  nav.addEventListener("click", (e) => {
    const btn = e.target.closest(".dot");
    if (!btn) return;

    e.preventDefault();
    const version = btn.dataset.version;

    slides.forEach((s) => {
      if (s.dataset.version === version) {
        s.hidden = false;
      } else {
        s.hidden = true;
      }
    });

    nav.querySelectorAll(".dot").forEach((el) =>
      el.classList.toggle("is-active", el === btn)
    );

    carousel.dataset.active = version;
  });
});