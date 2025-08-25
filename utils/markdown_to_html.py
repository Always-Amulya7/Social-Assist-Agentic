# utils/markdown_to_html.py
from markdown import markdown

def convert_md_to_html(md_text: str) -> str:
    """
    Converts markdown text to HTML for Gmail rendering.
    """
    return markdown(md_text, extensions=['extra', 'nl2br'])
