(() => {
  const PAGE = 24;
  const FEATURED = ["rsi", "workplace"];
  const savedView = localStorage.getItem("dab-view");
  const state = {
    lang:
      localStorage.getItem("dab-lang") ||
      ((navigator.language || "").startsWith("zh") ? "zh" : "en"),
    theme: localStorage.getItem("dab-theme") || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"),
    exact: localStorage.getItem("dab-exact") === "1",
    field: localStorage.getItem("dab-field") || "all",
    sort: localStorage.getItem("dab-sort") || (savedView === "heat" ? "cite" : "date"),
    shown: PAGE,
    data: null,
    index: null,
    query: "",
  };

  const els = {
    feed: document.getElementById("feed"),
    rail: document.getElementById("rail"),
    hero: document.getElementById("hero"),
    status: document.getElementById("status"),
    q: document.getElementById("q"),
    generated: document.getElementById("generated"),
    exact: document.getElementById("exact-match"),
  };

  function byDate(a, b) {
    return (b.announced_date || b.published || "").localeCompare(a.announced_date || a.published || "");
  }

  function setTheme(theme) {
    state.theme = theme;
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("dab-theme", theme);
    const btn = document.getElementById("theme-toggle");
    btn.textContent = t(state.lang, theme === "dark" ? "themeToLight" : "themeToDark");
    btn.setAttribute("aria-label", t(state.lang, "themeToggle"));
  }

  function setLang(lang) {
    state.lang = lang;
    localStorage.setItem("dab-lang", lang);
    applyStaticI18n(lang);
    document.querySelectorAll(".lang button").forEach((btn) => {
      btn.setAttribute("aria-pressed", String(btn.dataset.lang === lang));
    });
    setTheme(state.theme);
    render();
  }

  function setField(field) {
    state.field = field || "all";
    state.shown = PAGE;
    localStorage.setItem("dab-field", state.field);
    render();
  }

  function setSort(sort) {
    state.sort = sort === "cite" ? "cite" : "date";
    state.shown = PAGE;
    localStorage.setItem("dab-sort", state.sort);
    render();
  }

  function sortPapers(list) {
    const copy = [...list];
    if (state.sort === "cite") {
      copy.sort((a, b) => (b.citations || 0) - (a.citations || 0) || byDate(a, b));
    } else {
      copy.sort(byDate);
    }
    return copy;
  }

  function authorLine(paper) {
    const names = paper.authors || [];
    if (names.length <= 3) return names.join(", ");
    return `${names.slice(0, 3).join(", ")} et al.`;
  }

  function paperRow(paper, query, matchKind) {
    const title = query ? BM25.highlight(paper.title, query) : BM25.escapeHtml(paper.title);
    const absUrl = paper.links?.abs || `https://arxiv.org/abs/${paper.id}`;
    const cites = Number(paper.citations || 0);
    const rawAbs = paper.abstract || "";
    const absText = query ? BM25.highlight(rawAbs, query) : BM25.escapeHtml(rawAbs);
    const badge =
      matchKind === "exact"
        ? `<span class="chip chip--exact">${t(state.lang, "matchExact")}</span>`
        : matchKind === "cover"
          ? `<span class="chip chip--cover">${t(state.lang, "matchCover")}</span>`
          : "";
    const abstract = rawAbs
      ? `<div class="abstract" data-collapsed="true">
          <p>${absText}</p>
          <button type="button" data-abs aria-expanded="false">${t(state.lang, "expand")}</button>
        </div>`
      : "";
    return `
      <article class="row">
        <div class="row__main">
          <h3><a href="${absUrl}" target="_blank" rel="noopener">${title}</a></h3>
          <div class="meta">
            ${BM25.escapeHtml(paper.announced_date || "")}
            · <a href="${absUrl}" target="_blank" rel="noopener">${BM25.escapeHtml(paper.id)}</a>
            · ${BM25.escapeHtml(authorLine(paper))}
            ${badge}
          </div>
          ${abstract}
        </div>
        <div class="row__side">
          <span class="cite${cites ? "" : " cite--zero"}">
            <b>${cites}</b>
            <span>${t(state.lang, "citations")}</span>
          </span>
          <a class="row__go" href="${absUrl}" target="_blank" rel="noopener">${t(state.lang, "paperPage")}</a>
        </div>
      </article>
    `;
  }

  function moreButton(total) {
    if (state.shown >= total) return "";
    return `<button type="button" class="more" data-more>${t(state.lang, "loadMore")} (${state.shown} / ${total})</button>`;
  }

  function tabBar(groups) {
    const tabs = groups
      .map(([field, list]) => {
        const selected = field === state.field;
        const featured = FEATURED.includes(field) ? " tab--featured" : "";
        return `<button type="button" class="tab${featured}" role="tab" data-field="${field}" aria-selected="${selected}">${fieldLabel(field, state.lang)} <span class="n">${list.length}</span></button>`;
      })
      .join("");
    const sorts = [
      ["date", "sortDate"],
      ["cite", "sortCite"],
    ]
      .map(
        ([id, key]) =>
          `<button type="button" data-sort="${id}" aria-pressed="${id === state.sort}">${t(state.lang, key)}</button>`
      )
      .join("");
    return `
      <div class="toolbar">
        <div class="tabs" role="tablist">${tabs}</div>
        <div class="views" role="group" aria-label="${t(state.lang, "sortBy")}">${sorts}</div>
      </div>
    `;
  }

  function renderHero() {
    const total = state.data?.total || 0;
    const days = state.data?.days || [];
    const latest = days[0]?.date || "—";
    els.hero.innerHTML = `
      <h1>${t(state.lang, "docTitle")}</h1>
      <p>${t(state.lang, "heroLead")}</p>
      <div class="hero__stats">
        <div><b>${total}</b><span>${t(state.lang, "papers")}</span></div>
        <div><b>${days.length}</b><span>${t(state.lang, "days")}</span></div>
        <div><b>${latest}</b><span>${t(state.lang, "latest")}</span></div>
      </div>
    `;
    const stamp = state.data?.generated_at
      ? `${t(state.lang, "updated")} ${formatStamp(state.data.generated_at, state.lang)}`
      : "";
    els.generated.textContent = stamp;
  }

  function groupedFields(papers) {
    const groups = new Map();
    for (const paper of papers) {
      const field = paper.field || "other";
      if (!groups.has(field)) groups.set(field, []);
      groups.get(field).push(paper);
    }
    const featured = FEATURED.filter((id) => groups.has(id)).map((id) => [id, groups.get(id)]);
    const rest = [...groups.entries()]
      .filter(([id]) => !FEATURED.includes(id))
      .sort((a, b) => {
        if (a[0] === "other") return 1;
        if (b[0] === "other") return -1;
        return b[1].length - a[1].length;
      });
    return [["all", papers], ...featured, ...rest];
  }

  function renderRailFields(groups) {
    els.rail.innerHTML = groups
      .map(([field, list]) => {
        const current = field === state.field ? ' aria-current="true"' : "";
        return `<a href="#f-${field}" data-field="${field}"${current}><span>${fieldLabel(field, state.lang)}</span><span class="n">${list.length}</span></a>`;
      })
      .join("");
  }

  function renderFieldFeed() {
    const papers = state.data.papers || [];
    if (!papers.length) {
      els.feed.innerHTML = `<p class="status">${t(state.lang, "empty")}</p>`;
      return;
    }
    const groups = groupedFields(papers);
    if (!groups.some(([id]) => id === state.field)) {
      state.field = "all";
      localStorage.setItem("dab-field", "all");
    }
    renderRailFields(groups);
    const pair = groups.find(([id]) => id === state.field) || groups[0];
    const list = sortPapers(pair[1] || []);
    const slice = list.slice(0, state.shown);
    els.feed.innerHTML = `
      ${tabBar(groups)}
      <div class="day__head">
        <h2 id="f-${state.field}">${fieldLabel(state.field, state.lang)}</h2>
        <time>${list.length} ${t(state.lang, "papers")}</time>
      </div>
      <p class="search-head">${BM25.escapeHtml(fieldBlurb(state.field, state.lang))}</p>
      <div class="rows">${slice.map((p) => paperRow(p, "")).join("")}</div>
      ${moreButton(list.length)}
    `;
  }

  function renderSearch(query) {
    const hits = BM25.search(state.index, query, 80, { exact: state.exact });
    els.rail.innerHTML = "";
    if (!hits.length) {
      els.feed.innerHTML = `<p class="search-head">${t(state.lang, "noResults", query)}</p>`;
      return;
    }
    const slice = hits.slice(0, state.shown);
    els.feed.innerHTML = `
      <p class="search-head">${t(state.lang, "searchResults", hits.length, query)}</p>
      <div class="rows">${slice.map((hit) => paperRow(hit.paper, query, hit.match)).join("")}</div>
      ${moreButton(hits.length)}
    `;
  }

  function render() {
    if (!state.data) return;
    renderHero();
    if (els.exact) els.exact.checked = state.exact;
    if (state.query.trim()) renderSearch(state.query.trim());
    else renderFieldFeed();
  }

  function bind() {
    document.querySelectorAll(".lang button").forEach((btn) => {
      btn.addEventListener("click", () => setLang(btn.dataset.lang));
    });
    document.getElementById("theme-toggle").addEventListener("click", () => {
      setTheme(state.theme === "dark" ? "light" : "dark");
    });
    document.getElementById("search-form").addEventListener("submit", (ev) => ev.preventDefault());
    if (els.exact) {
      els.exact.checked = state.exact;
      els.exact.addEventListener("change", () => {
        state.exact = els.exact.checked;
        localStorage.setItem("dab-exact", state.exact ? "1" : "0");
        state.shown = PAGE;
        render();
      });
    }
    let timer = 0;
    els.q.addEventListener("input", () => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        state.query = els.q.value;
        state.shown = PAGE;
        render();
      }, 120);
    });
    document.addEventListener("keydown", (ev) => {
      if (ev.key === "/" && document.activeElement !== els.q && ev.target.tagName !== "INPUT") {
        ev.preventDefault();
        els.q.focus();
      }
      if (ev.key === "Escape") {
        if (state.query) {
          els.q.value = "";
          state.query = "";
          state.shown = PAGE;
          render();
        } else if (state.field && state.field !== "all") {
          setField("all");
        }
      }
    });
    els.feed.addEventListener("click", (ev) => {
      const more = ev.target.closest("[data-more]");
      if (more) {
        state.shown += PAGE;
        render();
        return;
      }
      const absBtn = ev.target.closest("[data-abs]");
      const collapsedAbs = ev.target.closest(".abstract[data-collapsed='true']");
      if (absBtn || collapsedAbs) {
        const box = (absBtn || collapsedAbs).closest(".abstract");
        const open = box.getAttribute("data-collapsed") !== "true";
        box.setAttribute("data-collapsed", open ? "true" : "false");
        const btn = box.querySelector("[data-abs]");
        if (btn) {
          btn.setAttribute("aria-expanded", String(!open));
          btn.textContent = t(state.lang, open ? "expand" : "collapse");
        }
        return;
      }
      const sortBtn = ev.target.closest("[data-sort]");
      if (sortBtn?.dataset.sort) {
        setSort(sortBtn.dataset.sort);
        return;
      }
      const tab = ev.target.closest("[data-field]");
      if (tab?.dataset.field) setField(tab.dataset.field);
    });
    els.rail.addEventListener("click", (ev) => {
      const link = ev.target.closest("[data-field]");
      if (link?.dataset.field) {
        ev.preventDefault();
        if (state.query) {
          els.q.value = "";
          state.query = "";
        }
        setField(link.dataset.field);
      }
    });
  }

  async function init() {
    setTheme(state.theme);
    applyStaticI18n(state.lang);
    document.querySelectorAll(".lang button").forEach((btn) => {
      btn.setAttribute("aria-pressed", String(btn.dataset.lang === state.lang));
    });
    bind();
    try {
      const res = await fetch("./data/index.json", { cache: "no-store" });
      if (!res.ok) throw new Error(String(res.status));
      state.data = await res.json();
      state.index = BM25.build(state.data.papers || []);
      els.status.hidden = true;
      render();
    } catch (err) {
      els.status.hidden = false;
      els.status.textContent = t(state.lang, "loadError");
      console.error(err);
    }
  }

  init();
})();
