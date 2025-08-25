import re, time, datetime as dt
from typing import List, Dict
import feedparser

YOUTUBE_RSS_BY_CHANNEL = "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
YOUTUBE_RSS_BY_USER = "https://www.youtube.com/feeds/videos.xml?user={user}"

def _extract_channel_id(handle: str) -> str:
    # Accept channel ID, channel URL, or @handle URL
    m = re.search(r"(UC[0-9A-Za-z_-]{22})", handle)
    if m:
        return m.group(1)
    m = re.search(r"youtube\.com/(channel/|@)([^/?#]+)", handle)
    if m and m.group(1) == "channel/":
        return m.group(2)
    # For @user, there's no RSS without resolving; try 'user' RSS
    return ""

def fetch_recent_videos(handle: str, lookback_hours: int = 48) -> List[Dict]:
    """
    Returns a list of dicts: {title, link, published, platform, author, description}
    """
    now = dt.datetime.utcnow()
    items = []
    channel_id = _extract_channel_id(handle)
    feeds = []
    if channel_id:
        feeds.append(YOUTUBE_RSS_BY_CHANNEL.format(channel_id=channel_id))
    else:
        # Try a user feed using the string after @ or the path end
        user = handle.replace("https://www.youtube.com/", "").strip("/")
        user = user.lstrip("@")
        feeds.append(YOUTUBE_RSS_BY_USER.format(user=user))

    for url in feeds:
        d = feedparser.parse(url)
        for e in d.entries[:30]:
            published = dt.datetime(*e.published_parsed[:6])
            age_h = (now - published).total_seconds() / 3600.0
            if age_h <= lookback_hours:
                items.append({
                    "platform": "youtube",
                    "title": e.title,
                    "link": e.link,
                    "published": published.isoformat() + "Z",
                    "author": getattr(e, "author", ""),
                    "description": getattr(e, "summary", ""),
                })
    return items