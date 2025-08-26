# import os
# import sys
# import yaml
# import datetime as dt
# import re
# from dotenv import load_dotenv
# from typing import List, Dict

# from utils.docx_parser import parse_handles_from_docx, parse_handles_from_csv
# from collectors.youtube_collector import fetch_recent_videos
# from collectors.instagram_collector import fetch_recent_posts
# from collectors.linkedin_collector import fetch_recent_items
# from reporting.report_builder import save_report, convert_md_to_html
# from reporting.email_sender import send_email
# from utils.scheduler import schedule_every

# import ollama

# # ------------------------------
# # CONFIGURATION
# # ------------------------------
# load_dotenv()
# CONFIG_PATH = "config.yaml" if os.path.exists("config.yaml") else "config.example.yaml"
# MODEL_NAME = "gpt-oss:20b"

# # ------------------------------
# # AI CHAT FUNCTION
# # ------------------------------
# def ai_chat(prompt: str) -> str:
#     print("\nAgent is thinking...")
#     response = ollama.chat(
#         model=MODEL_NAME,
#         messages=[{"role": "user", "content": prompt}],
#     )
#     return response.message.content.strip()

# # ------------------------------
# # CLEAN EMAIL
# # ------------------------------
# def extract_email(user_input: str) -> str:
#     match = re.search(r'[\w\.\+\-]+@[\w\.\-]+\.\w+', user_input)
#     if match:
#         return match.group(0)
#     return None

# # ------------------------------
# # AI-DRIVEN CONVERSATION
# # ------------------------------
# def ai_driven_conversation(config):
#     state = {}

#     # Greeting
#     print("Bot:", ai_chat("Greet the user in a friendly, professional, engaging way and tell that you are a Social Media Assistant Agent."))

#     # Name
#     print("Bot:", ai_chat("Ask the user their name. Output only the question."))
#     state["name"] = input("Me: ").strip()
#     print("Bot:", ai_chat(f"Hello {state['name']}! Nice to meet you."))

#     # Company
#     print("Bot:", ai_chat(f"Ask the person which company they are with. Output only the question."))
#     state["company"] = input("Me: ").strip()
#     print("Bot:", ai_chat(f"Great! So we’re working with {state['company']}. Give only in 15-20 words and never expose you are CHATGPT"))

#     # Email
#     print("Bot:", ai_chat(f"Ask the person for their email address. Output only the question."))
#     email_input = input("Me: ").strip()
#     email_clean = extract_email(email_input)
#     if not email_clean:
#         print("Bot: ❌ Invalid email. Please enter a valid email only.")
#         sys.exit(1)
#     state["email"] = email_clean
#     print("Bot:", f"Thank you for sharing your email address—{state['email']}. We’ve got it on file.")

#     # Gmail auth
#     client_secret = config["gmail"]["client_secret_file"]
#     if not os.path.exists(client_secret):
#         print("Bot: ⚠️ Gmail client secret file missing:", client_secret)
#         sys.exit(1)
#     print("Bot: ✅ Gmail credentials file found. Ready to send reports!")

#     # DOCX/CSV path
#     print("Bot:", ai_chat("Ask for the path to DOCX or CSV containing social media handles. Output only question."))
#     doc_path = input("Me: ").strip()
#     if not os.path.exists(doc_path):
#         print("Bot: ❌ File not found. Exiting.")
#         sys.exit(1)

#     if doc_path.lower().endswith(".docx"):
#         accounts = parse_handles_from_docx(doc_path)
#     else:
#         accounts = parse_handles_from_csv(doc_path)

#     accounts = [i for i in accounts if i["platform"].lower() in ("youtube","instagram","linkedin")]
#     if not accounts:
#         print("Bot: ⚠️ No valid accounts found. Exiting.")
#         sys.exit(1)

#     print(f"Bot: ✅ Parsed {len(accounts)} accounts:")
#     for acc in accounts:
#         print(f"   - {acc['platform'].capitalize()}: {acc['handle']}")

#     # Confirm fetch
#     print("Bot: Shall I fetch recent posts for these accounts? (Yes/No)")
#     fetch_confirm = input("Me: ").strip().lower() in ("yes","y")
#     if not fetch_confirm:
#         print("AI: 👍 Exiting now.")
#         return

#     lookback = int(config["analysis"].get("lookback_hours", 48))
#     items = search_web(accounts, lookback)

#     if not items:
#         print("Bot: ⚠️ No new content found. Using sample content for testing.")
#         items = [
#             {"platform":"youtube","handle":"PewDiePie","title":"Sample Video 1","description":"Sample description for testing."},
#             {"platform":"youtube","handle":"PewDiePie","title":"Sample Video 2","description":"Another test description."},
#         ]

#     # Analyze content
#     print("Bot: Shall I analyze the content? (Yes/No)")
#     analyze_confirm = input("Me: ").strip().lower() in ("yes","y")
#     if analyze_confirm:
#         analysis_results = analyze_content_with_ai(items)
#     else:
#         analysis_results = {"summary":"No analysis performed.", "items": items}

#     # Build report
#     report_md = build_report(state, lookback, analysis_results)  # <-- Fixed: pass full state dictionary
#     save_report(report_md,"data/reports")

#     # Send report
#     print("Bot: Do you want me to send this report via email now? (Yes/No)")
#     send_now = input("Me: ").strip().lower() in ("yes","y")
#     send_or_schedule(config, report_md, state["email"], send_now)

#     print("Bot: 👋 Done! Check your email or report folder for results.")
    
#     optional_chat()

# # ------------------------------
# # SEARCH SOCIAL MEDIA CONTENT
# # ------------------------------
# def search_web(accounts: List[Dict], lookback_hours: int) -> List[Dict]:
#     all_items=[]
#     print("\nBot: Searching for recent content...")
#     for acc in accounts:
#         platform, handle = acc["platform"].lower(), acc["handle"]
#         print(f"AI: Checking {platform.capitalize()} for {handle}...")
#         try:
#             if platform=="youtube":
#                 items = fetch_recent_videos(handle, lookback_hours)
#             elif platform=="instagram":
#                 items = fetch_recent_posts(handle, lookback_hours)
#             elif platform=="linkedin":
#                 items = fetch_recent_items(handle, lookback_hours)
#             else:
#                 items=[]
#         except Exception as e:
#             print(f"Bot: ⚠️ Error fetching {platform} {handle}: {e}")
#             items=[]
#         if items:
#             all_items.extend(items)
#     return all_items

# # ------------------------------
# # ANALYZE CONTENT WITH AI
# # ------------------------------
# def analyze_content_with_ai(items: List[Dict]) -> Dict:
#     combined_text = "\n".join(
#         [f"{it['platform']} {it['handle']} Title: {it['title']} Description: {it['description']}" for it in items]
#     )
#     prompt = (
#         "You are a professional social media analyst. Summarize the following content in Markdown format. "
#         "Include:- Executive Summary,Title, Description,Sentiment,Key Themes,Trends & Insights\n"
#         f"{combined_text}"
#     )
#     summary = ai_chat(prompt)
#     return {"summary": summary, "items": items}

# # ------------------------------
# # BUILD REPORT - CLEAN EMAIL FRIENDLY
# # ------------------------------
# def build_report(user_info: Dict, lookback: int, analysis: Dict) -> str:
#     now = dt.datetime.now().strftime("%B %d, %Y")
#     brand_name = user_info.get("company", "Brand")

#     high_level_summary = analysis.get("summary", "No significant trends identified.")
#     key_insights = analysis.get("takeaway", "No key insights generated.")
#     influencer_trends = "\n".join(
#         [f"- {item.get('key_themes','N/A')} (Platform: {item.get('platform','')}, Handle: {item.get('handle','')})"
#          for item in analysis.get("items", [])]
#     ) or "No influencer content found."
#     influencer_metrics = "\n".join(
#         [f"- {item.get('handle','N/A')}: {item.get('views','N/A')} views, {item.get('likes','N/A')} likes, {item.get('comments','N/A')} comments"
#          for item in analysis.get("items", [])]
#     ) or "No metrics available."
#     notable_posts = "\n".join(
#         [f"- {item.get('title','N/A')} ({item.get('platform','')})" for item in analysis.get("items", [])]
#     ) or "No notable posts available."

#     # Placeholder competitor & platform summaries
#     competitor_trends = "No competitor data provided."
#     competitor_strategy = "No strategic shifts detected."
#     competitor_opportunities = "No threats or opportunities identified."

#     yt_summary = "\n".join(
#         [f"- {item.get('title','N/A')}: {item.get('description','N/A')}" 
#          for item in analysis.get("items", []) if item.get('platform','').lower() == "youtube"]
#     ) or "No recent YouTube content."
#     ig_summary = "\n".join(
#         [f"- {item.get('title','N/A')}: {item.get('description','N/A')}" 
#          for item in analysis.get("items", []) if item.get('platform','').lower() == "instagram"]
#     ) or "No recent Instagram content."
#     li_summary = "\n".join(
#         [f"- {item.get('title','N/A')}: {item.get('description','N/A')}" 
#          for item in analysis.get("items", []) if item.get('platform','').lower() == "linkedin"]
#     ) or "No recent LinkedIn content."

#     # Sentiment breakdown
#     sent_pos = sum(1 for item in analysis.get("items", []) if item.get("sentiment","Neutral").lower()=="positive")
#     sent_neu = sum(1 for item in analysis.get("items", []) if item.get("sentiment","Neutral").lower()=="neutral")
#     sent_neg = sum(1 for item in analysis.get("items", []) if item.get("sentiment","Neutral").lower()=="negative")
#     total = max(len(analysis.get("items", [])), 1)  # avoid division by zero

#     actionable_insights = "Follow recommendations based on influencer and platform analysis."

#     # Overall Findings (list format, not table)
#     overall_findings = f"""
# ## OVERALL FINDINGS

# - **Sentiment:** Positive: {round(sent_pos/total*100)}% / Neutral: {round(sent_neu/total*100)}% / Negative: {round(sent_neg/total*100)}%
# - **Number of Items:** {len(analysis.get("items", []))}
# - **Common Themes:** {high_level_summary if high_level_summary else "N/A"}
# """

#     md = f"""
# # {brand_name} Social Media Intelligence Report
# **Report Date:** {now}
# **Analysis Period:** Last {lookback} Hours

# ---

# ## EXECUTIVE SUMMARY
# **Most Significant Trends Identified:**
# {high_level_summary}

# **Key Insights and Recommendations:**
# {key_insights}

# {overall_findings}

# ---

# ## INFLUENCER ANALYSIS
# **Content Themes and Topics:**
# {influencer_trends}

# **Engagement Metrics and Posting Frequency:**
# {influencer_metrics}

# **Sentiment Analysis:**
# - Positive: {round(sent_pos/total*100)}%
# - Neutral: {round(sent_neu/total*100)}%
# - Negative: {round(sent_neg/total*100)}%

# **Notable Content Examples:**
# {notable_posts}

# ---

# ## COMPETITOR ANALYSIS
# **Competitor Content Trends:**
# {competitor_trends}

# **Strategic Shifts:**
# {competitor_strategy}

# **Competitive Threats and Opportunities:**
# {competitor_opportunities}

# ---

# ## PLATFORM BREAKDOWN
# ### YouTube
# {yt_summary}

# ### Instagram
# {ig_summary}

# ### LinkedIn
# {li_summary}

# ---

# ## ACTIONABLE INSIGHTS
# **Recommended Actions Based on Findings:**
# {actionable_insights}

# ---

# **Monitoring Status:** Active across YouTube, Instagram, LinkedIn, and configured target accounts.
# """
#     return md

# # ------------------------------
# # SEND OR SCHEDULE EMAIL
# # ------------------------------
# def send_or_schedule(config, md_text, user_email, send_now=True):
#     html_text = convert_md_to_html(md_text)
#     sender = os.getenv("DEFAULT_FROM_NAME","Social Intelligence Agent")
#     subject = f"{config['brand']['name']} Social Media Report"
#     try:
#         if send_now:
#             send_email(
#                 config["gmail"]["client_secret_file"],
#                 config["gmail"]["token_file"],
#                 sender,
#                 [user_email, config["brand"]["team_email"]],
#                 subject,
#                 html_text,
#                 is_html=True
#             )
#             print("AI: ✅ Report sent successfully!")
#         else:
#             hours=int(config["reporting"].get("schedule_every_hours",48))
#             schedule_every(lambda: print("[Scheduled] Report executed"),hours)
#             print(f"Bot: ⏱️ Report scheduled every {hours} hours.")
#     except Exception as e:
#         print(f"Bot: ❌ Error sending email: {e}")

# # ------------------------------
# # OPTIONAL CHAT LOOP AT THE END
# # ------------------------------
# def optional_chat():
#     state = {}
#     choice = input("Do you want to have a chat with me? (Yes/No): ").strip().lower()
#     if choice not in ["yes", "y"]:
#         print("Bot: 👋 Okay! Goodbye.")
#         return

#     # Ask for name if not already stored
#     state["name"] = input("Me: ").strip()
#     print("Bot:", ai_chat(f"Hello {state['name']}! Nice to meet you."))

#     # Chat loop
#     while True:
#         user_input = input("Me: ").strip()
#         if user_input.lower() in ["exit", "quit", "no"]:
#             print("Bot: 👋 Goodbye!")
#             break
#         response = ai_chat(user_input)
#         print("Bot:", response)

# # ------------------------------
# # MAIN
# # ------------------------------
# def main():
#     try:
#         with open(CONFIG_PATH,"r",encoding="utf-8") as f:
#             config=yaml.safe_load(f)
#     except FileNotFoundError:
#         print("Bot: ❌ Configuration file not found. Exiting.")
#         sys.exit(1)
#     ai_driven_conversation(config)

# if __name__=="__main__":
#     main()

# Offline Version for the app

import os
import sys
import yaml
import datetime as dt
import re
from dotenv import load_dotenv
from typing import List, Dict

from utils.docx_parser import parse_handles_from_docx, parse_handles_from_csv
from collectors.youtube_collector import fetch_recent_videos
from collectors.instagram_collector import fetch_recent_posts
from collectors.linkedin_collector import fetch_recent_items
from reporting.report_builder import save_report, convert_md_to_html
from reporting.email_sender import send_email
from utils.scheduler import schedule_every

# ------------------------------
# CONFIGURATION
# ------------------------------
load_dotenv()
CONFIG_PATH = "config.yaml" if os.path.exists("config.yaml") else "config.example.yaml"

# ------------------------------
# CLEAN EMAIL EXTRACTION
# ------------------------------
def extract_email(user_input: str) -> str:
    match = re.search(r'[\w\.\+\-]+@[\w\.\-]+\.\w+', user_input)
    if match:
        return match.group(0)
    return None

# ------------------------------
# SEARCH SOCIAL MEDIA CONTENT
# ------------------------------
def search_web(accounts: List[Dict], lookback_hours: int) -> List[Dict]:
    all_items = []
    print("\nBot: Searching for recent content...")
    for acc in accounts:
        platform, handle = acc["platform"].lower(), acc["handle"]
        print(f"Bot: Checking {platform.capitalize()} for {handle}...")
        try:
            if platform == "youtube":
                items = fetch_recent_videos(handle, lookback_hours)
            elif platform == "instagram":
                items = fetch_recent_posts(handle, lookback_hours)
            elif platform == "linkedin":
                items = fetch_recent_items(handle, lookback_hours)
            else:
                items = []
        except Exception as e:
            print(f"Bot: ⚠️ Error fetching {platform} {handle}: {e}")
            items = []
        if items:
            all_items.extend(items)
    return all_items

# ------------------------------
# ANALYZE CONTENT
# ------------------------------
def analyze_content(items: List[Dict]) -> Dict:
    # For simplicity, just return items as analysis; can add AI logic here if needed
    return {"summary": "Analysis generated.", "items": items, "takeaway": "Review the detailed content below."}

# ------------------------------
# BUILD REPORT - CLEAN EMAIL FRIENDLY
# ------------------------------
def build_report(user_info: Dict, lookback: int, analysis: Dict) -> str:
    now = dt.datetime.now().strftime("%B %d, %Y")
    brand_name = user_info.get("company", "Brand")

    # Build influencer trends and metrics
    influencer_trends = "\n".join([f"- {item.get('key_themes','N/A')} (Platform: {item.get('platform','')}, Handle: {item.get('handle','')})"
                                   for item in analysis.get("items", [])]) or "No influencer content found."
    influencer_metrics = "\n".join([f"- {item.get('handle','N/A')}: {item.get('views','N/A')} views, {item.get('likes','N/A')} likes, {item.get('comments','N/A')} comments"
                                    for item in analysis.get("items", [])]) or "No metrics available."
    notable_posts = "\n".join([f"- {item.get('title','N/A')} ({item.get('platform','')})" for item in analysis.get("items", [])]) or "No notable posts available."

    # Sentiment counts
    sent_pos = sum(1 for item in analysis.get("items", []) if item.get("sentiment","Neutral").lower()=="positive")
    sent_neu = sum(1 for item in analysis.get("items", []) if item.get("sentiment","Neutral").lower()=="neutral")
    sent_neg = sum(1 for item in analysis.get("items", []) if item.get("sentiment","Neutral").lower()=="negative")
    total = max(len(analysis.get("items", [])), 1)

    md = f"""
# {brand_name} Social Media Intelligence Report
**Report Date:** {now}
**Analysis Period:** Last {lookback} Hours

---

## EXECUTIVE SUMMARY
**Most Significant Trends Identified:**
{analysis.get('summary', 'No significant trends identified.')}

**Key Insights and Recommendations:**
{analysis.get('takeaway', 'No key insights generated.')}

---

## INFLUENCER ANALYSIS
**Content Themes and Topics:**
{influencer_trends}

**Engagement Metrics and Posting Frequency:**
{influencer_metrics}

**Sentiment Analysis:**
- Positive: {round(sent_pos/total*100)}%
- Neutral: {round(sent_neu/total*100)}%
- Negative: {round(sent_neg/total*100)}%

**Notable Content Examples:**
{notable_posts}

---

## PLATFORM BREAKDOWN
### YouTube
{"\n".join([f"- {i.get('title','N/A')}: {i.get('description','N/A')}" for i in analysis.get("items", []) if i.get('platform','').lower()=="youtube"]) or "No recent YouTube content."}

### Instagram
{"\n".join([f"- {i.get('title','N/A')}: {i.get('description','N/A')}" for i in analysis.get("items", []) if i.get('platform','').lower()=="instagram"]) or "No recent Instagram content."}

### LinkedIn
{"\n".join([f"- {i.get('title','N/A')}: {i.get('description','N/A')}" for i in analysis.get("items", []) if i.get('platform','').lower()=="linkedin"]) or "No recent LinkedIn content."}

---

## ACTIONABLE INSIGHTS
**Recommended Actions Based on Findings:**
Follow recommendations based on influencer and platform analysis.

---

**Monitoring Status:** Active across YouTube, Instagram, LinkedIn, and configured target accounts.
"""
    return md

# ------------------------------
# SEND OR SCHEDULE EMAIL
# ------------------------------
def send_or_schedule(config, md_text, user_email, send_now=True):
    html_text = convert_md_to_html(md_text)
    sender = os.getenv("DEFAULT_FROM_NAME","Social Intelligence Agent")
    subject = f"{config['brand']['name']} Social Media Report"
    if send_now:
        send_email(
            config["gmail"]["client_secret_file"],
            config["gmail"]["token_file"],
            sender,
            [user_email, config["brand"]["team_email"]],
            subject,
            html_text,
            is_html=True
        )
        print("Bot: ✅ Report sent successfully!")
    else:
        hours=int(config["reporting"].get("schedule_every_hours",48))
        schedule_every(lambda: print("[Scheduled] Report executed"),hours)
        print(f"Bot: ⏱️ Report scheduled every {hours} hours.")

# ------------------------------
# OPTIONAL CHAT LOOP
# ------------------------------
def optional_chat():
    choice = input("Do you want to have a chat with me? (Yes/No): ").strip().lower()
    if choice not in ["yes", "y"]:
        print("Bot: 👋 Okay! Goodbye.")
        return

    name = input("Me: ").strip()
    print(f"Bot: Hello {name}! Nice to meet you.")

    while True:
        user_input = input("Me: ").strip()
        if user_input.lower() in ["exit", "quit", "no"]:
            print("Bot: 👋 Goodbye!")
            break
        # Placeholder simple echo; replace with AI call if needed
        print("Bot:", f"You said: {user_input}")

# ------------------------------
# AI-DRIVEN CONVERSATION (Python-only)
# ------------------------------
def ai_driven_conversation(config):
    state = {}

    state["name"] = input("Enter your full name: ").strip()
    state["company"] = input("Enter your company name: ").strip()
    email_input = input("Enter your email address: ").strip()
    email_clean = extract_email(email_input)
    if not email_clean:
        print("Bot: ❌ Invalid email. Exiting.")
        sys.exit(1)
    state["email"] = email_clean

    client_secret = config["gmail"]["client_secret_file"]
    if not os.path.exists(client_secret):
        print(f"Bot: ⚠️ Gmail client secret missing: {client_secret}")
        sys.exit(1)
    print("Bot: ✅ Gmail credentials found.")

    doc_path = input("Provide path to DOCX or CSV with social media handles: ").strip()
    if not os.path.exists(doc_path):
        print("Bot: ❌ File not found. Exiting.")
        sys.exit(1)
    if doc_path.lower().endswith(".docx"):
        accounts = parse_handles_from_docx(doc_path)
    else:
        accounts = parse_handles_from_csv(doc_path)
    accounts = [i for i in accounts if i["platform"].lower() in ("youtube","instagram","linkedin")]
    if not accounts:
        print("Bot: ⚠️ No valid accounts found. Exiting.")
        sys.exit(1)

    print(f"Bot: ✅ Parsed {len(accounts)} accounts:")
    for acc in accounts:
        print(f"   - {acc['platform'].capitalize()}: {acc['handle']}")

    fetch_confirm = input("Shall I fetch recent posts for these accounts? (Yes/No): ").strip().lower() in ("yes","y")
    if not fetch_confirm:
        print("Bot: 👍 Exiting now.")
        return

    lookback = int(config["analysis"].get("lookback_hours",48))
    items = search_web(accounts, lookback)
    if not items:
        print("Bot: ⚠️ No new content found. Using sample content.")
        items = [
            {"platform":"youtube","handle":"PewDiePie","title":"Sample Video 1","description":"Sample description for testing."},
            {"platform":"youtube","handle":"PewDiePie","title":"Sample Video 2","description":"Another test description."},
        ]

    analyze_confirm = input("Shall I analyze the content? (Yes/No): ").strip().lower() in ("yes","y")
    if analyze_confirm:
        analysis_results = analyze_content(items)
    else:
        analysis_results = {"summary":"No analysis performed.", "items": items, "takeaway":"No insights generated."}

    report_md = build_report(state, lookback, analysis_results)
    save_report(report_md,"data/reports")

    send_now = input("Do you want me to send this report via email now? (Yes/No): ").strip().lower() in ("yes","y")
    send_or_schedule(config, report_md, state["email"], send_now)

    print("Bot: 👋 Done! Check your email or report folder for results.")
    optional_chat()

# ------------------------------
# MAIN
# ------------------------------
def main():
    try:
        with open(CONFIG_PATH,"r",encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print("Bot: ❌ Configuration file not found. Exiting.")
        sys.exit(1)

    ai_driven_conversation(config)

if __name__=="__main__":
    main()
