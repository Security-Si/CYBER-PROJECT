(function () {
  const storageKey = "ssi_theme";
  const root = document.documentElement;

  function setButtonLabel(btn, theme) {
    if (!btn) return;
    btn.textContent = theme === "dark" ? "Clair" : "Sombre";
    btn.setAttribute("aria-label", theme === "dark" ? "Passer en mode clair" : "Passer en mode sombre");
  }

  function applyTheme(theme) {
    if (theme === "dark") root.setAttribute("data-theme", "dark");
    else root.removeAttribute("data-theme");
  }

  const btn = document.getElementById("themeToggle");
  const saved = localStorage.getItem(storageKey) || "light";
  applyTheme(saved);
  setButtonLabel(btn, saved);

  if (btn) {
    btn.addEventListener("click", () => {
      const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      localStorage.setItem(storageKey, next);
      applyTheme(next);
      setButtonLabel(btn, next);
    });
  }

  document.addEventListener("click", async (e) => {
    const target = e.target;
    if (!(target instanceof HTMLElement)) return;
    const copy = target.closest("[data-copy]");
    if (!copy) return;
    const selector = copy.getAttribute("data-copy");
    if (!selector) return;
    const el = document.querySelector(selector);
    if (!el) return;
    const text = (el.textContent || "").trimEnd();
    try {
      await navigator.clipboard.writeText(text);
      const old = copy.textContent;
      copy.textContent = "Copié";
      setTimeout(() => (copy.textContent = old || "Copier"), 900);
    } catch {
      // ignore
    }
  });
})();
