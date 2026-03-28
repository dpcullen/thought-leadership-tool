import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from config import RSS_FEEDS, SCRAPE_KEYWORDS


def fetch_rss_feeds():
    """Fetch and parse RSS feeds from tier-1 sources."""
    all_items = []

    for source_name, feed_url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:10]:
                published = ""
                if hasattr(entry, "published"):
                    published = entry.published
                elif hasattr(entry, "updated"):
                    published = entry.updated

                item = {
                    "source": source_name,
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "summary": entry.get("summary", "")[:500],
                    "published": published,
                }
                all_items.append(item)
        except Exception as e:
            all_items.append({
                "source": source_name,
                "title": f"[Feed error: {str(e)[:100]}]",
                "link": "",
                "summary": "",
                "published": "",
            })

    return all_items


def filter_relevant_items(items):
    """Filter items by keyword relevance to AI/SaaS space."""
    relevant = []
    for item in items:
        text = f"{item['title']} {item['summary']}".lower()
        matches = [kw for kw in SCRAPE_KEYWORDS if kw.lower() in text]
        if matches:
            item["matched_keywords"] = matches
            relevant.append(item)
    return relevant


def fetch_crunchbase_news():
    """Fetch recent funding/M&A news via web scraping."""
    items = []
    try:
        url = "https://news.crunchbase.com/venture/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            articles = soup.find_all("article", limit=10)
            for article in articles:
                title_tag = article.find(["h2", "h3"])
                link_tag = article.find("a", href=True)
                summary_tag = article.find("p")
                items.append({
                    "source": "Crunchbase News",
                    "title": title_tag.get_text(strip=True) if title_tag else "",
                    "link": link_tag["href"] if link_tag else "",
                    "summary": summary_tag.get_text(strip=True)[:500] if summary_tag else "",
                    "published": "",
                })
    except Exception as e:
        items.append({
            "source": "Crunchbase News",
            "title": f"[Scrape error: {str(e)[:100]}]",
            "link": "",
            "summary": "",
            "published": "",
        })
    return items


def gather_all_intel():
    """Gather all market intelligence from all sources."""
    rss_items = fetch_rss_feeds()
    relevant_rss = filter_relevant_items(rss_items)
    crunchbase = fetch_crunchbase_news()

    all_intel = relevant_rss + crunchbase

    # Format for digest generation
    formatted = "MARKET INTELLIGENCE GATHERED ON {}\n\n".format(
        datetime.now().strftime("%Y-%m-%d")
    )

    if not all_intel:
        formatted += "(No items gathered from feeds — you can paste intel manually below)\n"
        return formatted

    for i, item in enumerate(all_intel, 1):
        formatted += f"--- Item {i} ---\n"
        formatted += f"Source: {item['source']}\n"
        formatted += f"Title: {item['title']}\n"
        if item.get("link"):
            formatted += f"Link: {item['link']}\n"
        if item.get("summary"):
            formatted += f"Summary: {item['summary']}\n"
        if item.get("matched_keywords"):
            formatted += f"Keywords: {', '.join(item['matched_keywords'])}\n"
        formatted += "\n"

    return formatted
