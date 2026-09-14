"""Minimal arXiv Atom API client (stdlib only)."""

from __future__ import annotations

import email.utils
import http.client
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any

from config import (
    ARXIV_API,
    MAX_PAGES,
    PAGE_SIZE,
    QUERY_GAP_S,
    RATE_LIMIT_FLOOR_S,
    RATE_LIMIT_MAX_S,
    REQUEST_GAP_S,
    REQUEST_RETRIES,
    REQUEST_TIMEOUT_S,
    SEARCH_QUERIES,
    USER_AGENT,
)

ATOM = "{http://www.w3.org/2005/Atom}"
ARXIV_NS = "{http://arxiv.org/schemas/atom}"
OPENSEARCH = "{http://a9.com/-/spec/opensearch/1.1/}"

_ID_RE = re.compile(r"arxiv\.org/abs/(.+)$")


def _text(el: ET.Element | None) -> str:
    if el is None or el.text is None:
        return ""
    return re.sub(r"\s+", " ", el.text).strip()


def parse_arxiv_id(abs_url: str) -> str:
    m = _ID_RE.search(abs_url.strip())
    raw = m.group(1) if m else abs_url.rsplit("/", 1)[-1]
    return re.sub(r"v\d+$", "", raw)


def _parse_dt(value: str) -> str:
    if not value:
        return ""
    # arXiv timestamps look like 2026-08-24T18:03:11Z or with offset.
    try:
        if value.endswith("Z"):
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        else:
            dt = datetime.fromisoformat(value)
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return value


def entry_to_paper(entry: ET.Element) -> dict[str, Any]:
    abs_url = _text(entry.find(f"{ATOM}id"))
    arxiv_id = parse_arxiv_id(abs_url)
    links = {"abs": f"https://arxiv.org/abs/{arxiv_id}", "pdf": f"https://arxiv.org/pdf/{arxiv_id}"}
    html_abs = f"https://arxiv.org/html/{arxiv_id}"
    for link in entry.findall(f"{ATOM}link"):
        href = link.attrib.get("href", "")
        rel = link.attrib.get("rel", "")
        title = link.attrib.get("title", "")
        if title == "pdf" or href.endswith(".pdf"):
            links["pdf"] = href.replace("http://", "https://")
        elif rel == "alternate":
            links["abs"] = href.replace("http://", "https://")
    links["html"] = html_abs

    categories = []
    primary = ""
    primary_el = entry.find(f"{ARXIV_NS}primary_category")
    if primary_el is not None:
        primary = primary_el.attrib.get("term", "")
        if primary:
            categories.append(primary)
    for cat in entry.findall(f"{ATOM}category"):
        term = cat.attrib.get("term", "")
        if term and term not in categories:
            categories.append(term)

    authors = []
    for author in entry.findall(f"{ATOM}author"):
        name = _text(author.find(f"{ATOM}name"))
        if name:
            authors.append(name)

    published = _parse_dt(_text(entry.find(f"{ATOM}published")))
    updated = _parse_dt(_text(entry.find(f"{ATOM}updated")))
    announced = published[:10] if published else ""

    comment_el = entry.find(f"{ARXIV_NS}comment")
    doi_el = entry.find(f"{ARXIV_NS}doi")

    return {
        "id": arxiv_id,
        "title": _text(entry.find(f"{ATOM}title")),
        "abstract": _text(entry.find(f"{ATOM}summary")),
        "authors": authors,
        "categories": categories,
        "primary_category": primary or (categories[0] if categories else ""),
        "published": published,
        "updated": updated,
        "announced_date": announced,
        "comment": _text(comment_el) if comment_el is not None else "",
        "doi": _text(doi_el) if doi_el is not None else "",
        "links": links,
    }


def _in_window(paper: dict[str, Any], date_from: str, date_to: str) -> bool:
    day = paper.get("announced_date") or ""
    return bool(day) and date_from <= day <= date_to


def _submitted_date_clause(date_from: str, date_to: str) -> str:
    """Limit API search to the local date window so we don't hit huge result sets."""
    start = date_from.replace("-", "") + "0000"
    end = date_to.replace("-", "") + "2359"
    return f"submittedDate:[{start} TO {end}]"


_RETRYABLE = (
    TimeoutError,
    ConnectionResetError,
    BrokenPipeError,
    http.client.IncompleteRead,
    http.client.RemoteDisconnected,
    urllib.error.URLError,
)


def _backoff_s(attempt: int, rate_limited: bool = False) -> float:
    if rate_limited:
        return min(RATE_LIMIT_MAX_S, RATE_LIMIT_FLOOR_S * (2**attempt))
    return min(60.0, REQUEST_GAP_S * (2**attempt))


def _retry_after_s(exc: urllib.error.HTTPError) -> float | None:
    value = exc.headers.get("Retry-After")
    if not value:
        return None
    value = value.strip()
    if value.isdigit():
        return float(value)
    try:
        when = email.utils.parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return max(0.0, (when - datetime.now(timezone.utc)).total_seconds())


def _request(url: str, retries: int = REQUEST_RETRIES) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last_err: Exception | None = None
    for attempt in range(retries):
        rate_limited = False
        wait = _backoff_s(attempt)
        try:
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_S) as resp:
                return resp.read()
        except urllib.error.HTTPError as exc:
            last_err = exc
            if exc.code not in {429, 500, 502, 503, 504} or attempt + 1 >= retries:
                raise
            if exc.code == 429:
                rate_limited = True
                wait = _backoff_s(attempt, rate_limited=True)
                retry_after = _retry_after_s(exc)
                if retry_after is not None:
                    wait = max(wait, min(RATE_LIMIT_MAX_S, retry_after + 5.0))
                else:
                    wait = max(wait, RATE_LIMIT_FLOOR_S)
        except _RETRYABLE as exc:
            last_err = exc
            if attempt + 1 >= retries:
                raise
            wait = _backoff_s(attempt)
        print(f"  retry {attempt + 1}/{retries} in {wait:.0f}s ({last_err})", flush=True)
        time.sleep(wait)
    raise RuntimeError(f"arXiv request failed: {last_err}")


def _fetch_query(query: str, date_from: str, date_to: str, seen: set[str]) -> list[dict[str, Any]]:
    papers: list[dict[str, Any]] = []
    start = 0
    total = None
    reached_old = False
    windowed = f"({query}) AND {_submitted_date_clause(date_from, date_to)}"

    for page in range(MAX_PAGES):
        params = {
            "search_query": windowed,
            "start": start,
            "max_results": PAGE_SIZE,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
        url = ARXIV_API + "?" + urllib.parse.urlencode(params)
        if start:
            time.sleep(REQUEST_GAP_S)
        print(f"  GET start={start} {windowed[:90]}", flush=True)
        xml_bytes = _request(url)
        root = ET.fromstring(xml_bytes)
        if total is None:
            total_el = root.find(f"{OPENSEARCH}totalResults")
            total = int(_text(total_el) or "0")
            print(f"  totalResults={total}", flush=True)
        entries = root.findall(f"{ATOM}entry")
        if not entries:
            break
        for entry in entries:
            paper = entry_to_paper(entry)
            day = paper.get("announced_date") or ""
            if day and day < date_from:
                reached_old = True
                continue
            if paper["id"] in seen or not _in_window(paper, date_from, date_to):
                continue
            seen.add(paper["id"])
            papers.append(paper)
        start += PAGE_SIZE
        if reached_old or (total is not None and start >= total):
            break
    return papers


def fetch_by_ids(arxiv_ids: list[str]) -> list[dict[str, Any]]:
    ids = [parse_arxiv_id(i) if "/" in i or i.startswith("http") else i.strip() for i in arxiv_ids]
    ids = [i for i in ids if i]
    if not ids:
        return []
    papers: list[dict[str, Any]] = []
    for offset in range(0, len(ids), 20):
        chunk = ids[offset : offset + 20]
        if offset:
            time.sleep(REQUEST_GAP_S)
        params = {"id_list": ",".join(chunk), "max_results": len(chunk)}
        url = ARXIV_API + "?" + urllib.parse.urlencode(params)
        print(f"  GET id_list={','.join(chunk)}", flush=True)
        root = ET.fromstring(_request(url))
        for entry in root.findall(f"{ATOM}entry"):
            papers.append(entry_to_paper(entry))
    return papers


def fetch_window(date_from: str, date_to: str) -> list[dict[str, Any]]:
    seen: set[str] = set()
    papers: list[dict[str, Any]] = []
    failures = 0
    for i, query in enumerate(SEARCH_QUERIES):
        if i:
            time.sleep(QUERY_GAP_S)
        print(f"Query {i + 1}/{len(SEARCH_QUERIES)}", flush=True)
        try:
            papers.extend(_fetch_query(query, date_from, date_to, seen))
        except urllib.error.HTTPError as exc:
            failures += 1
            print(f"  query {i + 1} failed ({exc}); continuing with remaining queries", flush=True)
            if exc.code == 429:
                cool = min(RATE_LIMIT_MAX_S, RATE_LIMIT_FLOOR_S * 2)
                print(f"  cooling down {cool:.0f}s after rate limit", flush=True)
                time.sleep(cool)
            continue
        except (TimeoutError, urllib.error.URLError, RuntimeError) as exc:
            failures += 1
            print(f"  query {i + 1} failed ({exc}); continuing with remaining queries", flush=True)
            continue
    if not papers and failures:
        raise RuntimeError(f"arXiv fetch returned no papers after {failures} failed quer{'y' if failures == 1 else 'ies'}")
    if failures:
        print(f"Completed with partial results: {len(papers)} papers, {failures} failed quer{'y' if failures == 1 else 'ies'}", flush=True)
    papers.sort(key=lambda p: (p.get("published") or "", p.get("id") or ""), reverse=True)
    return papers
