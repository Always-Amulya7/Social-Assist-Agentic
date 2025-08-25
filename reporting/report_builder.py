import os, datetime as dt
import markdown

def save_report(markdown_text: str, dest_dir: str) -> str:
    os.makedirs(dest_dir, exist_ok=True)
    ts = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    path = os.path.join(dest_dir, f"{ts}_trend_brief.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(markdown_text)
    return path

def convert_md_to_html(md_text: str) -> str:
    return markdown.markdown(md_text)