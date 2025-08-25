from typing import List, Dict
import os, datetime as dt
from apify_client import ApifyClient

def fetch_recent_items(url: str, lookback_hours: int = 48) -> List[Dict]:
    """
    Uses an Apify actor to fetch recent posts from a LinkedIn profile/company page.
    Requires APIFY_TOKEN in env and a suitable actor configuration.
    Returns a normalized list similar to other collectors.
    """
    token = os.getenv("APIFY_TOKEN")
    if not token:
        return []  # disabled unless token provided
    client = ApifyClient(token)
    input = {
        "startUrls": [{"url": url}],
        "maxItems": 20,
    }
    run = client.actor("apify/linkedin-scraper").call(run_input=input)
    items = list(client.dataset(run["defaultDatasetId"]).list_items()["items"])
    now = dt.datetime.utcnow()
    out: List[Dict] = []
    for it in items:
        # Actor outputs vary; we normalize best-effort
        ts = it.get("time", it.get("datePosted"))
        if ts:
            try:
                published = dt.datetime.fromisoformat(ts.replace("Z","")).replace(tzinfo=None)
            except Exception:
                published = now
        else:
            published = now
        age_h = (now - published).total_seconds()/3600.0
        if age_h <= lookback_hours:
            out.append({
                "platform": "linkedin",
                "title": it.get("title") or (it.get("textContent","")[:120]),
                "link": it.get("url") or url,
                "published": published.isoformat() + "Z",
                "author": it.get("author",""),
                "description": it.get("textContent",""),
            })
    return out