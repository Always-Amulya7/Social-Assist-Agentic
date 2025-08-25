# analysis/analyzer.py
from typing import List, Dict, Tuple
from collections import defaultdict
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import yake
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer

# Download required NLTK data
try:
    _ = Tokenizer("english")
except LookupError:
    nltk.download("punkt_tab", quiet=True)
    
nltk.download("vader_lexicon", quiet=True)
nltk.download("punkt", quiet=True)


# ============================
# Summarize combined text
# ============================
def summarize_text(texts: List[str], max_sentences: int = 5) -> str:
    combined_text = " ".join([t for t in texts if t]).strip()
    if not combined_text:
        return "No significant content found during this period."
    # Use standard 'punkt' tokenizer
    parser = PlaintextParser.from_string(combined_text, Tokenizer("english"))
    summarizer = LexRankSummarizer()
    summary_sentences = summarizer(parser.document, max_sentences)
    return " ".join([str(s) for s in summary_sentences])

# ============================
# Extract top keywords using YAKE
# ============================
def extract_keywords(items: List[Dict], top_k: int = 10) -> List[str]:
    combined_texts = []
    for it in items:
        combined_texts.append((it.get("title", "") + " " + it.get("description", "")).strip())
    text = "\n".join(combined_texts).strip()
    if not text:
        return ["No prominent keywords"]
    kw_extractor = yake.KeywordExtractor(top=top_k, stopwords=None)
    keywords = kw_extractor.extract_keywords(text)
    return [k for k, score in keywords]

# ============================
# Sentiment scoring using VADER
# ============================
def sentiment_scores(items: List[Dict]) -> Tuple[float, float, float]:
    sia = SentimentIntensityAnalyzer()
    pos = neu = neg = 0
    n = 0
    for it in items:
        text = (it.get("title", "") + " " + it.get("description", "")).strip()
        if not text:
            continue
        score = sia.polarity_scores(text)
        pos += score["pos"]
        neu += score["neu"]
        neg += score["neg"]
        n += 1
    if n == 0:
        return 0.0, 100.0, 0.0
    return round(100 * pos / n, 1), round(100 * neu / n, 1), round(100 * neg / n, 1)

# ============================
# Find trends across platforms
# ============================
def find_trends(items: List[Dict]) -> List[str]:
    platform_texts = defaultdict(list)
    for it in items:
        platform_texts[it["platform"]].append((it.get("title", "") + " " + it.get("description", "")).strip())
    trends = []
    for plat, texts in platform_texts.items():
        kws = extract_keywords([{"title": t, "description": ""} for t in texts], top_k=8)
        if kws:
            trends.append(f"{plat.capitalize()}: {'; '.join(kws[:8])}")
    return trends if trends else ["No clear trends"]