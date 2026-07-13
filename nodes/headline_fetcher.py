"""
LangGraph LocalAI TV Pipeline — Headline Fetcher Node
Fetches news headlines from RSS feeds and news APIs with error recovery.
"""

import feedparser
import os
import json
from datetime import datetime
from typing import Optional


# Default RSS feeds for AP/TG news
DEFAULT_FEEDS = [
    "https://news.google.com/rss/search?q=Andhra+Pradesh&hl=en-IN&gl=IN&ceid=IN:en",
    "https://news.google.com/rss/search?q=Telangana&hl=en-IN&gl=IN&ceid=IN:en",
    "https://news.google.com/rss/search?q=India+technology&hl=en-IN&gl=IN&ceid=IN:en",
]


def fetch_headlines(
    feeds: Optional[list[str]] = None,
    max_headlines: int = 10,
    category: str = "general",
) -> list[dict]:
    """
    Fetch headlines from RSS feeds with error recovery.

    Args:
        feeds: List of RSS feed URLs. Uses defaults if None.
        max_headlines: Maximum number of headlines to return.
        category: News category filter.

    Returns:
        List of headline dicts with title, link, published, source, summary.
    """
    feeds = feeds or DEFAULT_FEEDS
    headlines = []

    for feed_url in feeds:
        try:
            parsed = feedparser.parse(feed_url)
            if parsed.bozo and not parsed.entries:
                print(f"  ⚠ Feed error for {feed_url}: {parsed.bozo_exception}")
                continue

            for entry in parsed.entries[:max_headlines]:
                headline = {
                    "title": entry.get("title", "Untitled"),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", datetime.now().isoformat()),
                    "source": entry.get("source", {}).get("title", feed_url),
                    "summary": entry.get("summary", "")[:300],
                    "category": category,
                    "fetched_at": datetime.now().isoformat(),
                }
                headlines.append(headline)

        except Exception as e:
            print(f"  ✗ Failed to fetch {feed_url}: {e}")
            continue

    # Deduplicate by title
    seen = set()
    unique = []
    for h in headlines:
        if h["title"] not in seen:
            seen.add(h["title"])
            unique.append(h)

    return unique[:max_headlines]


def filter_headlines(
    headlines: list[dict],
    keywords: Optional[list[str]] = None,
) -> list[dict]:
    """
    Filter headlines by keywords.

    Args:
        headlines: List of headline dicts.
        keywords: Keywords to filter by. Returns all if None.

    Returns:
        Filtered list of headlines.
    """
    if not keywords:
        return headlines

    filtered = []
    for h in headlines:
        text = f"{h['title']} {h['summary']}".lower()
        if any(kw.lower() in text for kw in keywords):
            filtered.append(h)

    return filtered
