#!/usr/bin/env python3
"""Read-only MCP server for the Maldives Government Gazette."""
from __future__ import annotations

import io
import json
import re
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlencode, urljoin, urlparse, urlunparse
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP

SITE = "https://www.gazette.gov.mv"
GAZETTE = f"{SITE}/gazette"
IULAAN = f"{SITE}/iulaan"
USER_AGENT = "gazette-mcp/1.0 (+read-only public research)"
TIMEOUT = 20
MAX_HTML = 3_000_000
MAX_PDF = 30_000_000
ALLOWED_TYPES = {"", "gaanoonu", "gavaaidhu", "garaaru", "usoolu", "other", "tax-ruling"}
TYPE_LABELS = {
    "": "all",
    "gaanoonu": "Law",
    "gavaaidhu": "Regulation",
    "garaaru": "Decision",
    "usoolu": "Procedure/Policy",
    "other": "Other",
    "tax-ruling": "Tax ruling",
}

IULAAN_TYPES = {
    "": "all",
    "masakkaiy": "Work/Projects",
    "gannan-beynunvaa": "Supplies wanted",
    "kuyyah-dhinun": "Property for rent",
    "kuyyah-hifun": "Property wanted",
    "vazeefaa": "Job opportunity",
    "thamreenu": "Training",
    "neelan": "Auction",
    "aanmu-mauloomaathu": "General information",
    "dhennevun": "Notice",
    "mubaaraaiy": "Competition",
    "noos-bayaan": "Press release",
    "insurance": "Insurance",
    "beelan": "Tender/Bid",
}

mcp = FastMCP("maldives-gazette")


def _fetch(url: str, *, max_bytes: int = MAX_HTML) -> tuple[int, str, bytes]:
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/pdf,*/*"})
    with urlopen(req, timeout=TIMEOUT) as response:
        data = response.read(max_bytes + 1)
        if len(data) > max_bytes:
            raise ValueError(f"response exceeded {max_bytes} byte safety limit")
        return int(response.status), response.headers.get("content-type", ""), data


def _safe_url(url: str, *, allow_pdf: bool = False) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise ValueError("only HTTPS URLs are allowed")
    host = (parsed.hostname or "").lower()
    path = parsed.path or "/"
    if host in {"www.gazette.gov.mv", "gazette.gov.mv"} and (path.startswith("/gazette") or path.startswith("/iulaan")):
        return url
    if allow_pdf and host == "storage.googleapis.com" and path.startswith("/gazette.gov.mv/docs/gazette/") and path.endswith(".pdf"):
        return url
    raise ValueError("URL is outside the public Gazette allowlist")


def _safe_attachment_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != "storage.googleapis.com":
        raise ValueError("attachment must use the official storage host")
    if not parsed.path.startswith("/gazette.gov.mv/docs/iulaan/"):
        raise ValueError("attachment is outside the official Iulaan attachment path")
    if not parsed.path.lower().endswith((".pdf", ".docx", ".doc", ".xlsx", ".xls")):
        raise ValueError("unsupported attachment type")
    return url


def _text(node: Any) -> str:
    return " ".join(node.get_text(" ", strip=True).split()) if node else ""


def _absolute(href: str, base: str = SITE) -> str:
    return urljoin(base, href)


def _record_from_item(item: Any) -> dict[str, Any] | None:
    title_link = item.select_one("a.gazette-title")
    if not title_link:
        return None
    title = _text(title_link)
    url = _absolute(title_link.get("href", ""))
    if not re.search(r"/gazette/\d+$", urlparse(url).path):
        return None
    category_link = item.select_one("a[href*='/gazette?type=']")
    pdf_link = item.select_one("a[href*='.pdf']")
    info = _text(item.select_one(".volume-info"))
    volume = issue = date = ""
    m = re.search(r"ވޮލިއުމް:\s*([^\s]+)", info)
    if m:
        volume = m.group(1)
    m = re.search(r"އަދަދު:\s*([^\s]+)", info)
    if m:
        issue = m.group(1)
    date_node = item.find(string=re.compile("ތާރީޚު"))
    if date_node:
        date_text = _text(date_node.parent.parent if getattr(date_node, "parent", None) else date_node)
        m = re.search(r"ތާރީޚު:\s*(.+?)(?:ވިދާޅުވޭ|$)", date_text)
        if m:
            date = m.group(1).strip()
    return {
        "title": title,
        "url": url,
        "category": _text(category_link) or None,
        "category_url": _absolute(category_link["href"]) if category_link and category_link.get("href") else None,
        "volume": volume or None,
        "issue": issue or None,
        "published_date": date or None,
        "pdf_url": _absolute(pdf_link["href"]) if pdf_link and pdf_link.get("href") else None,
        "source": url,
    }


def _parse_listing(html: bytes, url: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    records = []
    seen: set[str] = set()
    for item in soup.select(".items"):
        record = _record_from_item(item)
        if record and record["url"] not in seen:
            records.append(record)
            seen.add(record["url"])
    total_text = _text(soup.select_one("#gazette-main-wrapper"))
    total = None
    m = re.search(r"(?:Total|ޖުމްލަ)\s*([\d,]+)", total_text, re.I)
    if m:
        total = int(m.group(1).replace(",", ""))
    pages = []
    for a in soup.select("a[href*='/gazette?page=']"):
        href = _absolute(a.get("href", ""))
        if href not in pages:
            pages.append(href)
    return {"url": url, "total": total, "results": records, "pagination_urls": pages}


def _iulaan_record_from_item(item: Any) -> dict[str, Any] | None:
    title_link = item.select_one("a.iulaan-title")
    if not title_link:
        return None
    url = _absolute(title_link.get("href", ""))
    if not re.search(r"/iulaan/\d+$", urlparse(url).path):
        return None
    links = item.find_all("a", href=True)
    type_link = next((a for a in links if "type=" in a.get("href", "")), None)
    office_link = next((a for a in links if "office=" in a.get("href", "")), None)
    text = _text(item)
    published = deadline = ""
    match = re.search(r"ތާރީޚު:\s*(.+?)(?:ސުންގަޑި:|އިތުރަށް|$)", text)
    if match:
        published = match.group(1).strip()
    match = re.search(r"ސުންގަޑި:\s*(.+?)(?:އިތުރަށް|$)", text)
    if match:
        deadline = match.group(1).strip()
    return {
        "title": _text(title_link),
        "url": url,
        "type": _text(type_link) or None,
        "type_url": _absolute(type_link["href"]) if type_link else None,
        "office": _text(office_link) or None,
        "office_url": _absolute(office_link["href"]) if office_link else None,
        "published_date": published or None,
        "deadline": deadline or None,
        "source": url,
    }


def _parse_iulaan_listing(html: bytes, url: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in soup.select(".items"):
        record = _iulaan_record_from_item(item)
        if record and record["url"] not in seen:
            records.append(record)
            seen.add(record["url"])
    text = _text(soup.select_one(".items-list") or soup.body)
    total = None
    match = re.search(r"(?:ޖުމްލަ|Total)\s*([\d,]+)", text, re.I)
    if match:
        total = int(match.group(1).replace(",", ""))
    pages = []
    for a in soup.select("a[href*='/iulaan?page=']"):
        href = _absolute(a.get("href", ""))
        if href not in pages:
            pages.append(href)
    return {"url": url, "total": total, "results": records, "pagination_urls": pages}


def _iulaan_query_url(params: dict[str, Any]) -> str:
    clean = {key: str(value) for key, value in params.items() if value is not None and str(value) != ""}
    return f"{IULAAN}?{urlencode(clean)}" if clean else IULAAN


def _query_url(params: dict[str, Any]) -> str:
    clean: dict[str, str] = {}
    for key, value in params.items():
        if value is not None and str(value) != "":
            clean[key] = str(value)
    return f"{GAZETTE}?{urlencode(clean)}" if clean else GAZETTE


@mcp.tool()
def gazette_status() -> str:
    """Check whether the public Maldives Gazette website is reachable."""
    checked_at = datetime.now(timezone.utc).isoformat()
    try:
        status, content_type, body = _fetch(GAZETTE, max_bytes=MAX_HTML)
        return json.dumps({"ok": 200 <= status < 300, "status": status, "content_type": content_type, "bytes": len(body), "checked_at": checked_at, "source": GAZETTE}, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"ok": False, "error": type(exc).__name__, "message": str(exc), "checked_at": checked_at, "source": GAZETTE}, ensure_ascii=False)


@mcp.tool()
def gazette_categories() -> str:
    """List the public Gazette document categories supported by the site."""
    return json.dumps({"source": GAZETTE, "categories": [{"type": key, "label": label, "url": _query_url({"type": key})} for key, label in TYPE_LABELS.items()]}, ensure_ascii=False)


@mcp.tool()
def search_gazette(query: str = "", category: str = "", volume: str = "", issue: str = "", start_date: str = "", end_date: str = "", page: int = 1, max_results: int = 20) -> str:
    """Search public Gazette records by Dhivehi/Unicode keyword, category, volume, issue, dates, and page."""
    if category not in ALLOWED_TYPES:
        return json.dumps({"error": "invalid category", "allowed": sorted(ALLOWED_TYPES)}, ensure_ascii=False)
    if page < 1 or page > 751:
        return json.dumps({"error": "page must be between 1 and 751"}, ensure_ascii=False)
    max_results = max(1, min(max_results, 50))
    params = {"type": category, "volume": volume, "issue": issue, "q": query, "start-date": start_date, "end-date": end_date}
    if page > 1:
        params["page"] = page
    url = _query_url(params)
    try:
        status, _, body = _fetch(url)
        parsed = _parse_listing(body, url)
        parsed.update({"status": status, "query": query, "category": TYPE_LABELS.get(category, category), "requested_page": page})
        parsed["results"] = parsed["results"][:max_results]
        parsed["fetched_at"] = datetime.now(timezone.utc).isoformat()
        return json.dumps(parsed, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"error": type(exc).__name__, "message": str(exc), "url": url}, ensure_ascii=False)


@mcp.tool()
def get_gazette(url_or_id: str) -> str:
    """Read one public Gazette record page and return its metadata and official PDF URL."""
    url = url_or_id if url_or_id.startswith("http") else f"{GAZETTE}/{url_or_id.strip()}"
    try:
        url = _safe_url(url)
        status, _, body = _fetch(url)
        soup = BeautifulSoup(body, "html.parser")
        title = _text(soup.select_one(".iulaan-title, .gazette-title, h1, h2"))
        page_text = _text(soup.select_one(".additional-info") or soup.select_one(".container") or soup.body)
        pdf = soup.select_one("a[href*='.pdf']")
        values: dict[str, Any] = {"url": url, "status": status, "title": title or None, "pdf_url": _absolute(pdf["href"]) if pdf and pdf.get("href") else None, "source": url, "fetched_at": datetime.now(timezone.utc).isoformat()}
        info_values = [_text(node) for node in soup.select(".additional-info .info")]
        values["volume"] = next((x.split(":", 1)[1].strip() for x in info_values if x.startswith("ވޮލިއުމް:")), None)
        values["issue"] = next((x.split(":", 1)[1].strip() for x in info_values if x.startswith("އިޝޫ:")), None)
        values["published_date"] = next((x.split(":", 1)[1].strip() for x in info_values if x.startswith("ޕަބްލިޝްކުރި ތާރީޚު:")), None)
        return json.dumps(values, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"error": type(exc).__name__, "message": str(exc), "requested": url_or_id}, ensure_ascii=False)


@mcp.tool()
def browse_gazette(path: str = "/gazette", max_results: int = 20) -> str:
    """Browse a public Gazette path such as /gazette?page=2 or /gazette?type=gaanoonu."""
    url = _safe_url(_absolute(path))
    status, _, body = _fetch(url)
    parsed = _parse_listing(body, url)
    parsed.update({"status": status, "results": parsed["results"][:max(1, min(max_results, 50))], "fetched_at": datetime.now(timezone.utc).isoformat()})
    return json.dumps(parsed, ensure_ascii=False)


@mcp.tool()
def iulaan_categories() -> str:
    """List public Iulaan announcement categories, including tenders and job opportunities."""
    return json.dumps({"source": IULAAN, "categories": [{"type": key, "label": label, "url": _iulaan_query_url({"type": key})} for key, label in IULAAN_TYPES.items()]}, ensure_ascii=False)


@mcp.tool()
def search_iulaan(query: str = "", announcement_type: str = "", job_category: str = "", office: str = "", start_date: str = "", end_date: str = "", open_only: bool = False, page: int = 1, max_results: int = 20) -> str:
    """Search public Iulaan announcements for tenders, projects, jobs, suppliers, auctions, and notices."""
    if announcement_type not in IULAAN_TYPES:
        return json.dumps({"error": "invalid announcement_type", "allowed": sorted(IULAAN_TYPES)}, ensure_ascii=False)
    if page < 1 or page > 35152:
        return json.dumps({"error": "page must be between 1 and 35152"}, ensure_ascii=False)
    max_results = max(1, min(max_results, 50))
    params = {"type": announcement_type, "job-category": job_category, "office": office, "q": query, "start-date": start_date, "end-date": end_date}
    if open_only:
        params["open-only"] = 1
    if page > 1:
        params["page"] = page
    url = _iulaan_query_url(params)
    try:
        status, _, body = _fetch(url)
        parsed = _parse_iulaan_listing(body, url)
        parsed.update({"status": status, "query": query, "announcement_type": IULAAN_TYPES.get(announcement_type), "requested_page": page, "open_only": open_only, "fetched_at": datetime.now(timezone.utc).isoformat()})
        parsed["results"] = parsed["results"][:max_results]
        return json.dumps(parsed, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"error": type(exc).__name__, "message": str(exc), "url": url}, ensure_ascii=False)


@mcp.tool()
def get_iulaan(url_or_id: str) -> str:
    """Read one public Iulaan announcement and return its title, issuer, deadline, attachments, and source URL."""
    url = url_or_id if url_or_id.startswith("http") else f"{IULAAN}/{url_or_id.strip()}"
    try:
        url = _safe_url(url)
        status, _, body = _fetch(url)
        soup = BeautifulSoup(body, "html.parser")
        title = _text(soup.select_one(".iulaan-title, h1, h2"))
        info = [_text(node) for node in soup.select(".additional-info .info")]
        full_text = _text(soup.select_one(".iulaan-info") or soup.body)
        attachments = []
        for link in soup.select("a[href]"):
            href = _absolute(link["href"])
            if href.lower().endswith((".pdf", ".doc", ".docx", ".xls", ".xlsx")):
                attachments.append({"label": _text(link), "url": href})
        issuer_link = soup.select_one("a[href*='office=']")
        type_link = soup.select_one("a[href*='type=']")
        number = next((x.split(":", 1)[1].strip() for x in info if x.startswith("ނަންބަރު:")), None)
        published = next((x.split(":", 1)[1].strip() for x in info if x.startswith("ޕަބްލިޝްކުރި ތާރީޚު:")), None)
        deadline_match = re.search(r"ސުންގަޑި:\s*(.+?)(?:$|Tweet|Share)", full_text)
        values = {"url": url, "print_url": f"{IULAAN}/print/{urlparse(url).path.rsplit('/', 1)[-1]}", "status": status, "title": title or None, "announcement_number": number, "type": _text(type_link) or None, "issuer": _text(issuer_link) or None, "published_date": published, "deadline": deadline_match.group(1).strip() if deadline_match else None, "attachments": attachments, "source": url, "fetched_at": datetime.now(timezone.utc).isoformat()}
        return json.dumps(values, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"error": type(exc).__name__, "message": str(exc), "requested": url_or_id}, ensure_ascii=False)


def _extract_docx_text(data: bytes) -> str:
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        xml = archive.read("word/document.xml").decode("utf-8", "replace")
    xml = re.sub(r"</w:p>", "\n", xml)
    xml = re.sub(r"<[^>]+>", "", xml)
    return re.sub(r"\s+", " ", xml).strip()


@mcp.tool()
def read_iulaan_attachment(url: str, max_chars: int = 120000) -> str:
    """Extract text from an official Iulaan PDF or DOCX attachment for review."""
    try:
        url = _safe_attachment_url(url)
        max_chars = max(1000, min(max_chars, 250000))
        _, content_type, data = _fetch(url, max_bytes=MAX_PDF)
        suffix = Path(urlparse(url).path).suffix.lower()
        if suffix == ".pdf":
            with tempfile.TemporaryDirectory() as directory:
                source = Path(directory) / "source.pdf"
                output = Path(directory) / "output.txt"
                source.write_bytes(data)
                completed = subprocess.run(["pdftotext", "-layout", str(source), str(output)], capture_output=True, text=True, timeout=30)
                if completed.returncode != 0:
                    raise ValueError(completed.stderr.strip() or "pdftotext failed")
                text = output.read_text(errors="replace")
        elif suffix == ".docx":
            text = _extract_docx_text(data)
        else:
            return json.dumps({"error": "unsupported_text_extraction_type", "url": url, "content_type": content_type, "supported": [".pdf", ".docx"]}, ensure_ascii=False)
        return json.dumps({"url": url, "content_type": content_type, "characters": len(text), "truncated": len(text) > max_chars, "text": text[:max_chars], "source": url, "fetched_at": datetime.now(timezone.utc).isoformat()}, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"error": type(exc).__name__, "message": str(exc), "requested": url}, ensure_ascii=False)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
