#!/usr/bin/env python3
"""Fetch, classify, merge, and write the GitHub Pages data files."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from arxiv_client import fetch_by_ids, fetch_window  # noqa: E402
from citations import attach_citations  # noqa: E402
from classify import classify  # noqa: E402
from config import ARCHIVE_START  # noqa: E402
from site_pages import write_site  # noqa: E402
from summarize import build_report  # noqa: E402

ROOT = HERE.parent
DATA_DIR = ROOT / "docs" / "data"
INDEX_PATH = DATA_DIR / "index.json"


def utc_today() -> datetime:
    return datetime.now(timezone.utc)


def load_index() -> dict[str, Any]:
    if not INDEX_PATH.exists():
        return {"generated_at": "", "total": 0, "papers": [], "days": []}
    return json.loads(INDEX_PATH.read_text(encoding="utf-8"))


def paper_key(paper: dict[str, Any]) -> str:
    return paper["id"]


def merge_papers(existing: list[dict[str, Any]], incoming: list[dict[str, Any]], seen_on: str) -> list[dict[str, Any]]:
    by_id = {p["id"]: p for p in existing}
    for paper in incoming:
        prev = by_id.get(paper["id"])
        if prev is None:
            paper = dict(paper)
            paper["first_seen"] = paper.get("announced_date") or seen_on
            by_id[paper["id"]] = paper
            continue
        # Keep first_seen; refresh metadata if arXiv sent a newer version.
        merged = dict(prev)
        if (paper.get("updated") or "") >= (prev.get("updated") or ""):
            first_seen = prev.get("first_seen") or paper.get("announced_date") or seen_on
            citations = paper.get("citations")
            if citations is None:
                citations = prev.get("citations")
            merged.update(paper)
            merged["first_seen"] = first_seen
            if citations is not None:
                merged["citations"] = citations
        by_id[paper["id"]] = merged
    papers = list(by_id.values())
    papers.sort(key=lambda p: (p.get("published") or "", p.get("id") or ""), reverse=True)
    return papers


def build_payload(papers: list[dict[str, Any]], generated_at: str) -> dict[str, Any]:
    by_day: dict[str, list[dict[str, Any]]] = {}
    for paper in papers:
        day = paper.get("announced_date") or (paper.get("published") or "")[:10]
        if not day:
            continue
        by_day.setdefault(day, []).append(paper)

    days = []
    for date in sorted(by_day.keys(), reverse=True):
        day_papers = sorted(
            by_day[date],
            key=lambda p: (p.get("published") or "", p.get("id") or ""),
            reverse=True,
        )
        days.append(
            {
                "date": date,
                "count": len(day_papers),
                "report": build_report(date, day_papers),
                "paper_ids": [p["id"] for p in day_papers],
            }
        )

    slim_papers = []
    for p in papers:
        slim_papers.append(
            {
                "id": p["id"],
                "title": p.get("title") or "",
                "abstract": p.get("abstract") or "",
                "authors": p.get("authors") or [],
                "categories": p.get("categories") or [],
                "primary_category": p.get("primary_category") or "",
                "published": p.get("published") or "",
                "updated": p.get("updated") or "",
                "announced_date": p.get("announced_date") or "",
                "first_seen": p.get("first_seen") or "",
                "comment": p.get("comment") or "",
                "doi": p.get("doi") or "",
                "links": p.get("links") or {},
                "score": p.get("score") or 0,
                "tags": p.get("tags") or [],
                "field": p.get("field") or "other",
                "citations": int(p.get("citations") or 0),
            }
        )

    return {
        "generated_at": generated_at,
        "source": "arxiv",
        "total": len(slim_papers),
        "days": days,
        "papers": slim_papers,
    }


def write_payload(payload: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    # Per-day slices keep the site usable if the full index ever grows large.
    days_dir = DATA_DIR / "days"
    days_dir.mkdir(exist_ok=True)
    keep_days = {day["date"] for day in payload["days"]}
    for old in days_dir.glob("*.json"):
        if old.stem not in keep_days:
            old.unlink()
    papers_by_id = {p["id"]: p for p in payload["papers"]}
    for day in payload["days"]:
        day_papers = [papers_by_id[i] for i in day["paper_ids"] if i in papers_by_id]
        (days_dir / f"{day['date']}.json").write_text(
            json.dumps(
                {
                    "date": day["date"],
                    "count": day["count"],
                    "report": day["report"],
                    "papers": day_papers,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    meta = {
        "generated_at": payload["generated_at"],
        "total": payload["total"],
        "day_count": len(payload["days"]),
        "latest_date": payload["days"][0]["date"] if payload["days"] else "",
    }
    (DATA_DIR / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_site(payload, ROOT / "docs")


def run(
    days: int,
    backfill: int | None,
    replace: bool = False,
    reclassify: bool = False,
    since: str | None = None,
    skip_citations: bool = False,
    ids: list[str] | None = None,
) -> dict[str, Any]:
    today = utc_today().date()
    existing_index = load_index()
    existing = [] if replace else (existing_index.get("papers") or [])
    generated_at = utc_today().strftime("%Y-%m-%dT%H:%M:%SZ")

    if reclassify:
        accepted = []
        for paper in existing:
            classified = classify(paper)
            if classified is not None:
                accepted.append(classified)
        print(f"Reclassified {len(existing)} -> kept {len(accepted)}", flush=True)
        if not skip_citations:
            attach_citations(accepted)
        payload = build_payload(accepted, generated_at)
        write_payload(payload)
        print(
            f"Wrote {payload['total']} papers across {len(payload['days'])} days -> {INDEX_PATH}",
            flush=True,
        )
        return payload

    raw: list[dict[str, Any]] = []
    if ids:
        print(f"Fetching {len(ids)} arXiv id(s)", flush=True)
        raw.extend(fetch_by_ids(ids))

    if since or backfill is not None or not ids:
        if since:
            date_from = since
        elif backfill is not None:
            date_from = (today - timedelta(days=backfill)).isoformat()
        elif not existing:
            date_from = ARCHIVE_START
        else:
            date_from = (today - timedelta(days=days)).isoformat()
        date_to = today.isoformat()
        print(f"Fetching arXiv {date_from} -> {date_to}", flush=True)
        raw.extend(fetch_window(date_from, date_to))
    else:
        date_to = today.isoformat()
    print(f"API returned {len(raw)} candidate papers", flush=True)

    accepted: list[dict[str, Any]] = []
    for paper in raw:
        classified = classify(paper)
        if classified is not None:
            accepted.append(classified)
    print(f"Classifier kept {len(accepted)} agent-benchmark papers", flush=True)

    merged = merge_papers(existing, accepted, seen_on=date_to)
    if not skip_citations:
        attach_citations(merged)
    payload = build_payload(merged, generated_at)
    write_payload(payload)
    print(
        f"Wrote {payload['total']} papers across {len(payload['days'])} days → {INDEX_PATH}",
        flush=True,
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Update the daily agent-benchmark index.")
    parser.add_argument(
        "--days",
        type=int,
        default=4,
        help="Look back this many days (default 4, overlapping so late listings are caught).",
    )
    parser.add_argument(
        "--backfill",
        type=int,
        default=None,
        help="Look back this many days instead of --days (use for the first run).",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Rebuild the index from this fetch only (do not merge prior papers).",
    )
    parser.add_argument(
        "--reclassify",
        action="store_true",
        help="Filter the existing index with the current classifier; do not fetch.",
    )
    parser.add_argument(
        "--since",
        type=str,
        default=None,
        help="Fetch papers published on/after this YYYY-MM-DD (e.g. 2026-01-01).",
    )
    parser.add_argument(
        "--skip-citations",
        action="store_true",
        help="Do not query Semantic Scholar for citation counts.",
    )
    parser.add_argument(
        "--ids",
        type=str,
        default=None,
        help="Comma-separated arXiv ids to fetch and merge (e.g. 2606.05405).",
    )
    args = parser.parse_args()
    id_list = [i.strip() for i in args.ids.split(",") if i.strip()] if args.ids else None
    run(
        days=args.days,
        backfill=args.backfill,
        replace=args.replace,
        reclassify=args.reclassify,
        since=args.since,
        skip_citations=args.skip_citations,
        ids=id_list,
    )


if __name__ == "__main__":
    main()
