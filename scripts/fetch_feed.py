#!/usr/bin/env python3
"""Fetch the configured RSS feed and convert it to same-origin JSON for the widget."""

from __future__ import annotations

import html
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlparse

FEED_URL = "https://fetchrss.com/feed/1wiyX5B6DBvu1wiyWo7vWBbW.rss"
OUTPUT_FILE = Path(__file__).resolve().parents[1] / "feed.json"
MAX_ITEMS = 10
USER_AGENT = "EverAgCompanyNewsWidget/1.0 (+https://ever.ag/company-news)"

TAG_RE = re.compile(r"<[^>]+>")
IMG_RE = re.compile(r"<img[^>]+src=[\"']([^\"']+)[\"']", re.IGNORECASE)
WHITESPACE_RE = re.compile(r"\s+")


def text_of(node: ET.Element | None) -> str:
    return "" if node is None or node.text is None else node.text.strip()


def valid_http_url(value: str) -> str:
    value = html.unescape(value or "").strip()
    parsed = urlparse(value)
    return value if parsed.scheme in {"http", "https"} and parsed.netloc else ""


def clean_summary(raw_html: str, limit: int = 360) -> str:
    text = html.unescape(TAG_RE.sub(" ", raw_html or ""))
    text = WHITESPACE_RE.sub(" ", text).strip()
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    if len(text) <= limit:
        return text
    return text[: limit - 1].rsplit(" ", 1)[0] + "…"


def normalize_date(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    try:
        parsed = parsedate_to_datetime(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc).isoformat()
    except (TypeError, ValueError, OverflowError):
        pass
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc).isoformat()
    except ValueError:
        return value


def find_first(node: ET.Element, names: list[str]) -> ET.Element | None:
    for name in names:
        found = node.find(name)
        if found is not None:
            return found
    return None


def extract_image(item: ET.Element, description_html: str) -> str:
    media_namespaces = [
        "{http://search.yahoo.com/mrss/}content",
        "{http://search.yahoo.com/mrss/}thumbnail",
    ]
    for tag in media_namespaces:
        for node in item.findall(tag):
            url = valid_http_url(node.attrib.get("url", ""))
            if url:
                return url

    for enclosure in item.findall("enclosure"):
        kind = enclosure.attrib.get("type", "").lower()
        url = valid_http_url(enclosure.attrib.get("url", ""))
        if url and (not kind or kind.startswith("image/")):
            return url

    match = IMG_RE.search(description_html or "")
    return valid_http_url(match.group(1)) if match else ""


def parse_rss(root: ET.Element) -> list[dict[str, str]]:
    channel = root.find("channel") if root.tag.lower().endswith("rss") else root
    if channel is None:
        channel = root

    nodes = channel.findall("item")
    if not nodes:
        nodes = root.findall(".//{http://www.w3.org/2005/Atom}entry")

    items: list[dict[str, str]] = []
    for node in nodes[:MAX_ITEMS]:
        title = text_of(find_first(node, ["title", "{http://www.w3.org/2005/Atom}title"]))
        description_node = find_first(
            node,
            [
                "description",
                "{http://purl.org/rss/1.0/modules/content/}encoded",
                "{http://www.w3.org/2005/Atom}summary",
                "{http://www.w3.org/2005/Atom}content",
            ],
        )
        description_html = text_of(description_node)

        link = text_of(node.find("link"))
        if not link:
            atom_link = node.find("{http://www.w3.org/2005/Atom}link")
            if atom_link is not None:
                link = atom_link.attrib.get("href", "")

        date_node = find_first(
            node,
            [
                "pubDate",
                "{http://purl.org/dc/elements/1.1/}date",
                "{http://www.w3.org/2005/Atom}published",
                "{http://www.w3.org/2005/Atom}updated",
            ],
        )

        item = {
            "title": html.unescape(title),
            "link": valid_http_url(link),
            "date": normalize_date(text_of(date_node)),
            "summary": clean_summary(description_html),
            "image": extract_image(node, description_html),
        }
        if item["title"] or item["link"]:
            items.append(item)
    return items


def main() -> int:
    request = urllib.request.Request(FEED_URL, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            xml_bytes = response.read()
        root = ET.fromstring(xml_bytes)
        items = parse_rss(root)
        if not items:
            raise RuntimeError("The RSS feed contained no usable items.")

        payload = {
            "source": FEED_URL,
            "fetchedAt": datetime.now(timezone.utc).isoformat(),
            "items": items,
        }
        OUTPUT_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {len(items)} items to {OUTPUT_FILE}")
        return 0
    except Exception as exc:
        print(f"Feed update failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
