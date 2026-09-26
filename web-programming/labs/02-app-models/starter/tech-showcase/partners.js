document.querySelectorAll("[data-partners-slider]").forEach((slider) => {
  const viewport = slider.querySelector("[data-partners-viewport]");
  const previous = slider.querySelector('[data-action="partners-previous"]');
  const next = slider.querySelector('[data-action="partners-next"]');

  const updateControls = () => {
    const end = viewport.scrollWidth - viewport.clientWidth;
    previous.disabled = viewport.scrollLeft <= 2;
    next.disabled = viewport.scrollLeft >= end - 2;
  };

  const scroll = (direction) => {
    viewport.scrollBy({
      left: direction * viewport.clientWidth,
      behavior: "smooth",
    });
  };

  previous.addEventListener("click", () => scroll(-1));
  next.addEventListener("click", () => scroll(1));
  viewport.addEventListener("scroll", updateControls, { passive: true });
  window.addEventListener("resize", updateControls);
  updateControls();
});
