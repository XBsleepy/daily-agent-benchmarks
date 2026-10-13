"""Static HTML, sitemap, and feed output so crawlers can read the site without JS."""

from __future__ import annotations

import json
import re
from datetime import date
from html import escape
from pathlib import Path
from typing import Any

from config import FIELD_LABELS, REPO_URL, SITE_URL, THEME_LABELS

SITE_NAME = "Daily Agent Benchmarks"
SITE_TAGLINE = "New LLM agent benchmarks on arXiv, updated daily"
SITE_DESCRIPTION = (
    "Daily Agent Benchmarks: a daily, searchable index of new AI agent benchmark papers on arXiv: LLM agents, "
    "web and GUI agents, coding / SWE agents, tool use, computer use, multi-agent, "
    "embodied and safety evaluations. Titles, authors, abstracts, citations, and PDF links."
)
KEYWORDS = (
    "agent benchmark, LLM agent benchmark, AI agent evaluation, agentic benchmark, "
    "web agent, GUI agent, computer use, coding agent, SWE benchmark, tool use, "
    "multi-agent, arXiv, daily papers"
)
HOME_LIMIT = 40
FEED_LIMIT = 50
RELATED_LIMIT = 8

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com" />\n'
    '    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
    "    <link\n"
    '      href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;'
    "0,6..72,600;0,6..72,700;1,6..72,400&family=Public+Sans:ital,wght@0,400;0,500;0,600;1,400"
    '&display=swap"\n'
    '      rel="stylesheet"\n'
    "    />"
)


def safe_id(pid: str) -> str:
    # arXiv ids can contain '/' for old papers; flatten to a filename.
    return pid.replace("/", "_")


def page_path(pid: str) -> str:
    return f"p/{safe_id(pid)}.html"


def page_url(pid: str) -> str:
    return SITE_URL + page_path(pid)


def abs_url(paper: dict[str, Any]) -> str:
    return (paper.get("links") or {}).get("abs") or f"https://arxiv.org/abs/{paper['id']}"


def pdf_url(paper: dict[str, Any]) -> str:
    return (paper.get("links") or {}).get("pdf") or f"https://arxiv.org/pdf/{paper['id']}"


def html_url(paper: dict[str, Any]) -> str:
    return (paper.get("links") or {}).get("html") or f"https://arxiv.org/html/{paper['id']}"


def day_of(paper: dict[str, Any]) -> str:
    return paper.get("announced_date") or (paper.get("published") or "")[:10]


def human_date(iso: str) -> str:
    try:
        d = date.fromisoformat(iso[:10])
    except ValueError:
        return iso
    return f"{d.strftime('%B')} {d.day}, {d.year}"


def field_label(field: str) -> str:
    return (FIELD_LABELS.get(field) or FIELD_LABELS["other"])["en"]


def tag_label(tag: str) -> str:
    return (THEME_LABELS.get(tag) or {"en": tag})["en"]


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def snippet(text: str, limit: int = 160) -> str:
    text = clean(text)
    if len(text) <= limit:
        return text
    cut = text[: limit - 1].rsplit(" ", 1)[0].rstrip(",;:.")
    return cut + "…"


def author_line(paper: dict[str, Any], limit: int | None = None) -> str:
    names = paper.get("authors") or []
    if limit and len(names) > limit:
        return ", ".join(names[:limit]) + " et al."
    return ", ".join(names)


def json_ld(data: Any) -> str:
    raw = json.dumps(data, ensure_ascii=False, indent=2).replace("</", "<\\/")
    return f'<script type="application/ld+json">\n{raw}\n    </script>'


def write_if_changed(path: Path, text: str) -> None:
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return
    path.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------- paper pages

PAPER_PAGE = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title} | {site}</title>
    <meta name="description" content="{description}" />
    <meta name="keywords" content="{keywords}" />
    <link rel="canonical" href="{url}" />
    <meta property="og:site_name" content="{site}" />
    <meta property="og:type" content="article" />
    <meta property="og:title" content="{title}" />
    <meta property="og:description" content="{description}" />
    <meta property="og:url" content="{url}" />
    <meta property="article:published_time" content="{published}" />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="{title}" />
    <meta name="twitter:description" content="{description}" />
    <link rel="alternate" type="application/atom+xml" title="{site}" href="../feed.xml" />
    <link rel="icon" href="../favicon.svg" type="image/svg+xml" />
    {fonts}
    <link rel="stylesheet" href="../css/style.css" />
    {ld}
    <script>window.PAPER_ID = {id_json}; window.PAPER_BASE = "../";</script>
  </head>
  <body>
    <header class="masthead masthead--simple">
      <div class="masthead__brand">
        <a class="wordmark" href="../">
          <span>
            <span class="wordmark__kicker">arXiv daily</span>
            <span class="wordmark__title">Agent Benchmarks</span>
          </span>
        </a>
      </div>
    </header>
    <main id="main" class="paper-page">
      <p class="crumb"><a href="../">All benchmarks</a> · <a href="../archive.html">Archive</a></p>
      <article class="paper paper--full">
        <h1>{title}</h1>
        <div class="meta">
          {authors}
          · {pid}
          · <time datetime="{day}">{day}</time>
          · {field}{cites}
        </div>
        {tags}
        <div class="abstract" data-collapsed="false">
          <p>{abstract}</p>
        </div>
        <div class="links">
          <a href="{abs}" target="_blank" rel="noopener">Abstract page</a>
          <a href="{pdf}" target="_blank" rel="noopener">PDF</a>
          <a href="{html}" target="_blank" rel="noopener">HTML</a>
        </div>
      </article>
    </main>
    {related}
    <footer class="colophon">
      <p class="colophon__meta">
        <span>
          <span data-i18n="visitorsPage">Page views</span>
          <strong id="vercount_value_page_pv">-</strong>
          ·
          <strong id="vercount_value_site_uv">-</strong>
          <span data-i18n="visitorsSite">visitors</span>
        </span>
        <a href="../archive.html">Archive</a>
        <a href="{repo}" target="_blank" rel="noopener">GitHub</a>
      </p>
    </footer>
    <script defer src="https://events.vercount.one/js"></script>
    <script src="../js/i18n.js"></script>
    <script src="../js/bm25.js"></script>
    <script src="../js/paper.js"></script>
  </body>
</html>
"""


def paper_ld(paper: dict[str, Any]) -> dict[str, Any]:
    data: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "ScholarlyArticle",
        "headline": clean(paper.get("title") or "")[:110],
        "name": clean(paper.get("title") or ""),
        "abstract": clean(paper.get("abstract") or ""),
        "author": [{"@type": "Person", "name": n} for n in paper.get("authors") or []],
        "datePublished": paper.get("published") or day_of(paper),
        "dateModified": paper.get("updated") or paper.get("published") or day_of(paper),
        "url": page_url(paper["id"]),
        "mainEntityOfPage": page_url(paper["id"]),
        "sameAs": [abs_url(paper)],
        "identifier": {"@type": "PropertyValue", "propertyID": "arXiv", "value": paper["id"]},
        "keywords": list(
            dict.fromkeys([field_label(paper.get("field") or "other"), *(tag_label(t) for t in paper.get("tags") or []), "agent benchmark"])
        ),
        "about": ["AI agent benchmark", field_label(paper.get("field") or "other")],
        "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": SITE_URL},
        "encoding": {"@type": "MediaObject", "encodingFormat": "application/pdf", "contentUrl": pdf_url(paper)},
    }
    if paper.get("doi"):
        data["sameAs"].append(f"https://doi.org/{paper['doi']}")
    return data


def related_block(paper: dict[str, Any], related: list[dict[str, Any]]) -> str:
    if not related:
        return ""
    items = "\n".join(
        f'          <li><a href="{escape(safe_id(p["id"]))}.html"><strong>{escape(clean(p.get("title") or ""))}</strong></a>'
        f" <span>{escape(day_of(p))}</span></li>"
        for p in related
    )
    label = escape(field_label(paper.get("field") or "other"))
    return f"""<nav class="paper-page related" aria-label="Related benchmarks">
      <h2>More {label} benchmarks</h2>
      <ol class="highlights">
{items}
      </ol>
    </nav>"""


def render_paper_page(paper: dict[str, Any], related: list[dict[str, Any]]) -> str:
    title = escape(clean(paper.get("title") or paper["id"]))
    tags = paper.get("tags") or []
    tag_html = (
        '<div class="themes">' + "".join(f'<span class="chip">{escape(tag_label(t))}</span>' for t in tags) + "</div>"
        if tags
        else ""
    )
    cites = int(paper.get("citations") or 0)
    field = field_label(paper.get("field") or "other")
    keywords = ", ".join(dict.fromkeys([field, *(tag_label(t) for t in tags), "agent benchmark", "LLM agent", "arXiv", paper["id"]]))
    return PAPER_PAGE.format(
        title=title,
        site=SITE_NAME,
        description=escape(f"{SITE_NAME}: " + snippet(paper.get("abstract") or paper.get("title") or "", 135)),
        keywords=escape(keywords),
        url=escape(page_url(paper["id"])),
        published=escape(paper.get("published") or day_of(paper)),
        fonts=FONTS,
        ld=json_ld(paper_ld(paper)),
        id_json=json.dumps(paper["id"]),
        authors=escape(author_line(paper)),
        pid=escape(paper["id"]),
        day=escape(day_of(paper)),
        field=escape(field),
        cites=f" · {cites} citations" if cites else "",
        tags=tag_html,
        abstract=escape(clean(paper.get("abstract") or "")),
        abs=escape(abs_url(paper)),
        pdf=escape(pdf_url(paper)),
        html=escape(html_url(paper)),
        related=related_block(paper, related),
        repo=REPO_URL,
    )


def related_map(papers: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Nearest papers (by date) in the same field, so every page links to its neighbours."""
    by_field: dict[str, list[dict[str, Any]]] = {}
    for p in sorted(papers, key=lambda p: (day_of(p), p["id"]), reverse=True):
        by_field.setdefault(p.get("field") or "other", []).append(p)
    out: dict[str, list[dict[str, Any]]] = {}
    half = RELATED_LIMIT // 2
    for group in by_field.values():
        for i, p in enumerate(group):
            lo = max(0, min(i - half, len(group) - RELATED_LIMIT - 1))
            window = group[lo : lo + RELATED_LIMIT + 1]
            out[p["id"]] = [q for q in window if q["id"] != p["id"]][:RELATED_LIMIT]
    return out


def write_paper_pages(papers: list[dict[str, Any]], paper_dir: Path) -> None:
    paper_dir.mkdir(parents=True, exist_ok=True)
    related = related_map(papers)
    keep = set()
    for paper in papers:
        keep.add(safe_id(paper["id"]))
        write_if_changed(
            paper_dir / f"{safe_id(paper['id'])}.html",
            render_paper_page(paper, related.get(paper["id"], [])),
        )
    for old in paper_dir.glob("*.html"):
        if old.stem not in keep:
            old.unlink()


# ---------------------------------------------------------------- home page

SEO_START, SEO_END = "<!-- seo:start -->", "<!-- seo:end -->"
STATIC_START, STATIC_END = "<!-- static:start -->", "<!-- static:end -->"


def replace_between(text: str, start: str, end: str, body: str) -> str:
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if not pattern.search(text):
        raise ValueError(f"marker {start!r} not found")
    return pattern.sub(lambda _: f"{start}\n{body}\n    {end}", text, count=1)


def home_seo(payload: dict[str, Any], latest: list[dict[str, Any]]) -> str:
    title = f"{SITE_NAME} — {SITE_TAGLINE}"
    ld = [
        {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": SITE_NAME,
            "alternateName": ["Agent Benchmarks Daily", "每日 Agent Benchmark"],
            "url": SITE_URL,
            "description": SITE_DESCRIPTION,
            "inLanguage": ["en", "zh-Hans"],
            "sameAs": [REPO_URL],
        },
        {
            "@context": "https://schema.org",
            "@type": "Dataset",
            "name": f"{SITE_NAME} index",
            "description": SITE_DESCRIPTION,
            "url": SITE_URL,
            "keywords": [k.strip() for k in KEYWORDS.split(",")],
            "isAccessibleForFree": True,
            "license": "https://arxiv.org/help/license",
            "creator": {"@type": "Organization", "name": SITE_NAME, "url": REPO_URL},
            "dateModified": payload.get("generated_at") or "",
            "temporalCoverage": f"{payload['days'][-1]['date']}/{payload['days'][0]['date']}" if payload.get("days") else "",
            "distribution": [
                {"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": SITE_URL + "data/index.json"}
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": "Latest agent benchmarks",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "url": page_url(p["id"]), "name": clean(p.get("title") or "")}
                for i, p in enumerate(latest)
            ],
        },
    ]
    desc = escape(SITE_DESCRIPTION)
    return f"""    <title>{escape(title)}</title>
    <meta name="description" content="{desc}" />
    <meta name="keywords" content="{escape(KEYWORDS)}" />
    <link rel="canonical" href="{SITE_URL}" />
    <meta property="og:site_name" content="{SITE_NAME}" />
    <meta property="og:title" content="{escape(title)}" />
    <meta property="og:description" content="{desc}" />
    <meta property="og:type" content="website" />
    <meta property="og:url" content="{SITE_URL}" />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="{escape(title)}" />
    <meta name="twitter:description" content="{desc}" />
    <link rel="alternate" type="application/atom+xml" title="{SITE_NAME}" href="./feed.xml" />
    <link rel="sitemap" type="application/xml" href="./sitemap.xml" />
    {json_ld(ld)}"""


def static_row(paper: dict[str, Any], base: str) -> str:
    cites = int(paper.get("citations") or 0)
    return f"""          <article class="row">
            <div class="row__main">
              <h3><a href="{base}{page_path(paper['id'])}">{escape(clean(paper.get('title') or ''))}</a></h3>
              <div class="meta">{escape(day_of(paper))} · <a href="{escape(abs_url(paper))}">{escape(paper['id'])}</a> · {escape(author_line(paper, 3))} · {escape(field_label(paper.get('field') or 'other'))}</div>
              <div class="abstract" data-collapsed="true"><p>{escape(snippet(paper.get('abstract') or '', 320))}</p></div>
            </div>
            <div class="row__side"><span class="cite{'' if cites else ' cite--zero'}"><b>{cites}</b><span>citations</span></span></div>
          </article>"""


def home_static(payload: dict[str, Any], latest: list[dict[str, Any]]) -> str:
    days = payload.get("days") or []
    latest_day = days[0]["date"] if days else "—"
    report = (days[0].get("report") or {}).get("en", {}) if days else {}
    summary = escape(report.get("summary") or "")
    rows = "\n".join(static_row(p, "./") for p in latest)
    return f"""        <section class="hero" id="hero">
          <h1>{SITE_NAME}</h1>
          <p>A once-a-day reading list of new agent benchmarks on arXiv — LLM agents, web and GUI agents, coding agents, tool use, computer use, multi-agent, embodied and safety evaluations.</p>
          <div class="hero__stats">
            <div><b>{payload.get('total', 0)}</b><span>papers</span></div>
            <div><b>{len(days)}</b><span>days</span></div>
            <div><b>{latest_day}</b><span>latest drop</span></div>
          </div>
        </section>
        <div id="status" class="status" hidden></div>
        <div id="feed" class="feed">
          <div class="day__head">
            <h2>Latest agent benchmarks</h2>
            <time datetime="{latest_day}">{escape(human_date(latest_day))}</time>
          </div>
          <p class="search-head">{summary} <a href="./archive.html">Browse the full archive</a>.</p>
          <div class="rows">
{rows}
          </div>
        </div>"""


def write_home(payload: dict[str, Any], index_html: Path) -> None:
    latest = sorted(payload.get("papers") or [], key=lambda p: (day_of(p), p["id"]), reverse=True)[:HOME_LIMIT]
    text = index_html.read_text(encoding="utf-8")
    text = replace_between(text, SEO_START, SEO_END, home_seo(payload, latest))
    text = replace_between(text, STATIC_START, STATIC_END, home_static(payload, latest))
    write_if_changed(index_html, text)


# ---------------------------------------------------------------- archive

ARCHIVE_PAGE = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Archive: all {total} agent benchmark papers | {site}</title>
    <meta name="description" content="{description}" />
    <link rel="canonical" href="{url}" />
    <meta property="og:site_name" content="{site}" />
    <meta property="og:title" content="Archive of agent benchmark papers" />
    <meta property="og:description" content="{description}" />
    <meta property="og:type" content="website" />
    <meta property="og:url" content="{url}" />
    <link rel="alternate" type="application/atom+xml" title="{site}" href="./feed.xml" />
    <link rel="icon" href="./favicon.svg" type="image/svg+xml" />
    {fonts}
    <link rel="stylesheet" href="./css/style.css" />
    <script>
      document.documentElement.dataset.theme =
        localStorage.getItem("dab-theme") ||
        (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    </script>
  </head>
  <body>
    <header class="masthead masthead--simple">
      <div class="masthead__brand">
        <a class="wordmark" href="./">
          <span>
            <span class="wordmark__kicker">arXiv daily</span>
            <span class="wordmark__title">Agent Benchmarks</span>
          </span>
        </a>
      </div>
    </header>
    <main id="main" class="paper-page">
      <p class="crumb"><a href="./">All benchmarks</a></p>
      <h1>Agent benchmark archive</h1>
      <p>{total} agent benchmark papers from arXiv across {day_count} announcement days, newest first. Each entry links to a summary page with the abstract, authors, and PDF.</p>
{months}
    </main>
    <footer class="colophon">
      <p class="colophon__meta">
        <a href="./">Home</a>
        <a href="./feed.xml">Atom feed</a>
        <a href="{repo}" target="_blank" rel="noopener">GitHub</a>
        <a href="https://arxiv.org" target="_blank" rel="noopener">arXiv.org</a>
      </p>
    </footer>
  </body>
</html>
"""


def write_archive(payload: dict[str, Any], out: Path) -> None:
    by_id = {p["id"]: p for p in payload.get("papers") or []}
    months: dict[str, list[dict[str, Any]]] = {}
    for day in payload.get("days") or []:
        months.setdefault(day["date"][:7], []).append(day)
    blocks = []
    for month, days in months.items():
        label = date.fromisoformat(month + "-01").strftime("%B %Y")
        parts = [f'      <section class="day" id="m-{month}">\n        <h2>{label}</h2>']
        for day in days:
            items = "\n".join(
                f'          <li><a href="./{page_path(pid)}"><strong>{escape(clean(by_id[pid].get("title") or ""))}</strong></a>'
                f' <span>{escape(field_label(by_id[pid].get("field") or "other"))}</span></li>'
                for pid in day["paper_ids"]
                if pid in by_id
            )
            parts.append(
                f'        <h3 id="d-{day["date"]}"><time datetime="{day["date"]}">{human_date(day["date"])}</time>'
                f' · {day["count"]}</h3>\n        <ol class="highlights">\n{items}\n        </ol>'
            )
        parts.append("      </section>")
        blocks.append("\n".join(parts))
    total = payload.get("total", 0)
    write_if_changed(
        out,
        ARCHIVE_PAGE.format(
            total=total,
            day_count=len(payload.get("days") or []),
            site=SITE_NAME,
            description=escape(
                f"Daily Agent Benchmarks archive: browse all {total} AI agent benchmark papers collected from arXiv, grouped by month and "
                "announcement day: web, GUI, coding, tool-use, multi-agent, embodied, and safety benchmarks."
            ),
            url=SITE_URL + "archive.html",
            fonts=FONTS,
            months="\n".join(blocks),
            repo=REPO_URL,
        ),
    )


# ---------------------------------------------------------------- sitemap / feed / llms.txt


def write_sitemap(payload: dict[str, Any], out: Path) -> None:
    latest = (payload.get("days") or [{}])[0].get("date", "")
    urls = [(SITE_URL, latest, "daily", "1.0"), (SITE_URL + "archive.html", latest, "daily", "0.8")]
    for p in payload.get("papers") or []:
        mod = (p.get("updated") or p.get("published") or day_of(p))[:10]
        urls.append((page_url(p["id"]), mod, "monthly", "0.6"))
    body = "\n".join(
        f"  <url><loc>{escape(u)}</loc><lastmod>{m}</lastmod><changefreq>{c}</changefreq><priority>{pr}</priority></url>"
        for u, m, c, pr in urls
    )
    write_if_changed(
        out,
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "\n</urlset>\n",
    )


def write_feed(payload: dict[str, Any], out: Path) -> None:
    papers = sorted(payload.get("papers") or [], key=lambda p: (day_of(p), p["id"]), reverse=True)[:FEED_LIMIT]
    entries = []
    for p in papers:
        authors = "".join(f"<author><name>{escape(n)}</name></author>" for n in (p.get("authors") or [])[:10])
        entries.append(
            f"""  <entry>
    <title>{escape(clean(p.get('title') or ''))}</title>
    <link href="{escape(page_url(p['id']))}" />
    <link rel="related" href="{escape(abs_url(p))}" />
    <id>{escape(page_url(p['id']))}</id>
    <published>{escape(p.get('published') or day_of(p))}</published>
    <updated>{escape(p.get('updated') or p.get('published') or day_of(p))}</updated>
    {authors}
    <category term="{escape(field_label(p.get('field') or 'other'))}" />
    <summary>{escape(clean(p.get('abstract') or ''))}</summary>
  </entry>"""
        )
    write_if_changed(
        out,
        f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>{SITE_NAME}</title>
  <subtitle>{escape(SITE_TAGLINE)}</subtitle>
  <link href="{SITE_URL}" />
  <link rel="self" href="{SITE_URL}feed.xml" />
  <id>{SITE_URL}</id>
  <updated>{escape(payload.get('generated_at') or '')}</updated>
{chr(10).join(entries)}
</feed>
""",
    )


def write_llms_txt(payload: dict[str, Any], out: Path) -> None:
    """llms.txt: a plain-markdown map of the site for LLM crawlers and answer engines."""
    lines = [
        f"# {SITE_NAME}",
        "",
        f"> {SITE_DESCRIPTION}",
        "",
        "Papers are pulled from the arXiv API once a day, filtered to LLM / AI agent benchmarks, "
        "and grouped by arXiv announcement day. Each paper has a static page with title, authors, "
        "abstract, field, citation count, and links to the arXiv abstract, PDF, and HTML versions.",
        "",
        "## Site",
        "",
        f"- [Home]({SITE_URL}): latest agent benchmarks with BM25 search",
        f"- [Archive]({SITE_URL}archive.html): every paper grouped by month and day",
        f"- [Atom feed]({SITE_URL}feed.xml): latest {FEED_LIMIT} papers",
        f"- [JSON index]({SITE_URL}data/index.json): full machine-readable data",
        f"- [Source code]({REPO_URL})",
        "",
        "## Papers",
        "",
    ]
    for p in sorted(payload.get("papers") or [], key=lambda p: (day_of(p), p["id"]), reverse=True):
        lines.append(
            f"- [{clean(p.get('title') or '')}]({page_url(p['id'])}): arXiv {p['id']}, "
            f"{day_of(p)}, {field_label(p.get('field') or 'other')}"
        )
    write_if_changed(out, "\n".join(lines) + "\n")


def write_site(payload: dict[str, Any], docs: Path) -> None:
    write_paper_pages(payload.get("papers") or [], docs / "p")
    write_home(payload, docs / "index.html")
    write_archive(payload, docs / "archive.html")
    write_sitemap(payload, docs / "sitemap.xml")
    write_feed(payload, docs / "feed.xml")
    write_llms_txt(payload, docs / "llms.txt")
