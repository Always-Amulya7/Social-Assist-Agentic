from typing import List, Dict
import datetime as dt
import instaloader

def fetch_recent_posts(username: str, lookback_hours: int = 48) -> List[Dict]:
    """
    Uses instaloader to fetch public posts and filter by time window.
    Returns: [{platform, title, link, published, author, description}]
    """
    L = instaloader.Instaloader(download_pictures=False, download_videos=False, save_metadata=False, dirname_pattern="/tmp")
    # Anonymous: works for public profiles; for private/login, uncomment and set environment vars.
    # L.login(USERNAME, PASSWORD)
    try:
        profile = instaloader.Profile.from_username(L.context, username.strip("@"))
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"Profile {username} does not exist.")
        return []

    now = dt.datetime.utcnow()
    results = []
    for post in profile.get_posts():
        published = post.date_utc.replace(tzinfo=None)
        age_h = (now - published).total_seconds() / 3600.0
        if age_h <= lookback_hours:
            results.append({
                "platform": "instagram",
                "title": (post.caption or "").split("\n")[0][:120],
                "link": f"https://www.instagram.com/p/{post.shortcode}/",
                "published": published.isoformat() + "Z",
                "author": profile.username,
                "description": post.caption or "",
            })
        else:
            break
    return results