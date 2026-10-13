(() => {
  const base = window.PAPER_BASE || "./";
  const lang =
    localStorage.getItem("dab-lang") ||
    ((navigator.language || "").startsWith("zh") ? "zh" : "en");
  const theme =
    localStorage.getItem("dab-theme") ||
    (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");

  document.documentElement.dataset.theme = theme;
  // Keep the prerendered <title>; applyStaticI18n would reset it to the site title.
  const staticTitle = document.title;
  applyStaticI18n(lang);
  document.title = staticTitle;

  function paperId() {
    if (window.PAPER_ID) return window.PAPER_ID;
    const q = new URLSearchParams(location.search).get("id");
    if (q) return q;
    const m = location.pathname.match(/\/p\/(.+)\.html$/);
    return m ? decodeURIComponent(m[1]).replace(/_/g, "/") : "";
  }

  function authorLine(paper) {
    const names = paper.authors || [];
    return names.join(", ");
  }

  async function init() {
    const id = paperId();
    const root = document.getElementById("main");
    // Static pages already contain the paper; only show errors on the empty fallback page.
    const prerendered = Boolean(root.querySelector("article"));
    const fail = () => {
      if (!prerendered) root.innerHTML = `<p class="status">${t(lang, "loadError")}</p>`;
    };
    try {
      const res = await fetch(`${base}data/index.json`, { cache: "no-store" });
      if (!res.ok) throw new Error(String(res.status));
      const data = await res.json();
      const paper = (data.papers || []).find((item) => item.id === id);
      if (!paper) {
        fail();
        return;
      }
      document.title = `${paper.title} | ${t("en", "docTitle")}`;
      const absUrl = paper.links?.abs || `https://arxiv.org/abs/${paper.id}`;
      const pdfUrl = paper.links?.pdf || `https://arxiv.org/pdf/${paper.id}`;
      const htmlUrl = paper.links?.html || `https://arxiv.org/html/${paper.id}`;
      const tags = (paper.tags || [])
        .map((tag) => `<span class="chip">${BM25.escapeHtml(tag)}</span>`)
        .join("");
      const cites = Number(paper.citations || 0);
      root.innerHTML = `
        <p class="crumb"><a href="${base}">${t(lang, "backHome")}</a> · <a href="${base}archive.html">${t(lang, "archive")}</a></p>
        <article class="paper paper--full">
          <h1>${BM25.escapeHtml(paper.title)}</h1>
          <div class="meta">
            ${BM25.escapeHtml(authorLine(paper))}
            · ${BM25.escapeHtml(paper.id)}
            · ${BM25.escapeHtml(paper.announced_date || "")}
            · ${BM25.escapeHtml(fieldLabel(paper.field || "other", lang))}
            ${cites ? ` · ${cites} ${t(lang, "citations")}` : ""}
          </div>
          ${tags ? `<div class="themes">${tags}</div>` : ""}
          <div class="abstract" data-collapsed="false">
            <p>${BM25.escapeHtml(paper.abstract)}</p>
          </div>
          <div class="links">
            <a href="${absUrl}" target="_blank" rel="noopener">${t(lang, "abs")}</a>
            <a href="${pdfUrl}" target="_blank" rel="noopener">${t(lang, "pdf")}</a>
            <a href="${htmlUrl}" target="_blank" rel="noopener">${t(lang, "html")}</a>
          </div>
        </article>
      `;
    } catch (err) {
      fail();
      console.error(err);
    }
  }

  init();
})();
