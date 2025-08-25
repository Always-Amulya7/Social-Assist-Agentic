import os
import yaml
import datetime as dt
import json
import re
import ollama
from dotenv import load_dotenv
from typing import List, Dict
from utils.docx_parser import parse_handles_from_docx, parse_handles_from_csv
from collectors.youtube_collector import fetch_recent_videos
from collectors.instagram_collector import fetch_recent_posts
from collectors.linkedin_collector import fetch_recent_items
from reporting.report_builder import save_report, convert_md_to_html
from reporting.email_sender import send_email
from utils.scheduler import schedule_every

load_dotenv()
CONFIG_PATH = "config.yaml"
if not os.path.exists(CONFIG_PATH):
    CONFIG_PATH = "config.example.yaml"

MODEL_NAME = "gpt-oss:20b"  # Ollama local model

# ---------------- AI Utilities ----------------
def get_ai_message(prompt: str) -> str:
    response = ollama.chat(model=MODEL_NAME, messages=[{"role": "user", "content": prompt}])
    message = response.message.content.strip()
    print(f"AI: {message}\n")
    return message

def ai_input(prompt: str) -> str:
    """Ask the user a question via AI, then return user reply."""
    ai_message = get_ai_message(prompt)
    reply = input("Me: ").strip()
    return reply

def parse_ai_json(text: str) -> dict:
    if not text:
        return {}
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            return {}
    return {}

# ---------------- Content & Analysis ----------------
def fetch_social_content(accounts: List[Dict], lookback_hours: int) -> List[Dict]:
    all_items = []
    for acc in accounts:
        plat, handle = acc["platform"].lower(), acc["handle"]
        try:
            if plat == "youtube": items = fetch_recent_videos(handle, lookback_hours)
            elif plat == "instagram": items = fetch_recent_posts(handle, lookback_hours)
            elif plat == "linkedin": items = fetch_recent_items(handle, lookback_hours)
            else: items = []
        except:
            items = []
        if not items:
            items = [{"platform": plat, "handle": handle, "title": f"Sample {plat} post",
                      "description": f"Dummy content for {handle}"}]
        all_items.extend(items)
    return all_items

def analyze_content_with_ollama(items: List[Dict]):
    content_text = "\n".join([f"{it['platform']} - {it['handle']}: {it['title']}. {it.get('description','')}" for it in items])
    analysis_prompt = f"""
You are a Social Media Intelligence Analyst AI.
Analyze the following posts:

{content_text}

Tasks:
1. High-level summary
2. Top 5 influencer content themes
3. Cross-account trends
4. Sentiment (pos/neu/neg %)
5. List 5 notable posts
6. AI reasoning / thinking
7. Conversation type per post

Respond strictly in JSON:
- high_level_summary
- influencer_trends
- trends_list
- sentiment: {{pos:int, neu:int, neg:int}}
- notable_posts
- ai_thinking
- conversation_types (handle, platform, type)
"""
    response = get_ai_message(analysis_prompt)
    print("AI: Analysis completed\n")
    return parse_ai_json(response)

# ---------------- Report Generation ----------------
def build_md_report(user_data, analysis_results):
    now = dt.datetime.now().strftime("%B %d, %Y")
    formatted_influencer_trends = ", ".join(analysis_results.get('influencer_trends',[]))
    notable_posts = "\n".join(analysis_results.get('notable_posts',[])) or "None"
    conversation_types = "\n".join([f"- {ct['handle']} ({ct['platform']}): {ct['type']}" for ct in analysis_results.get('conversation_types',[])]) or "None"

    md = f"""
# **{user_data.get('company','Unknown Company')} Social Media Intelligence Report**

**Report Date:** {now}  
**Analysis Period:** Last {user_data.get('lookback_hours',48)} Hours  

---

## **EXECUTIVE SUMMARY**
{analysis_results.get('high_level_summary','No summary')}

---

## **INFLUENCER ANALYSIS**
**Content Themes and Topics:** {formatted_influencer_trends}

**Notable Content:**
{notable_posts}

---

## **CROSS-ACCOUNT TRENDS**
{analysis_results.get('trends_list',[])}

---

## **SENTIMENT ANALYSIS**
- Positive: {analysis_results.get('sentiment',{}).get('pos',0)}%
- Neutral: {analysis_results.get('sentiment',{}).get('neu',0)}%
- Negative: {analysis_results.get('sentiment',{}).get('neg',0)}%

---

## **AI THINKING / REASONING**
{analysis_results.get('ai_thinking','No reasoning available')}

---

## **CONVERSATION TYPES**
{conversation_types}

---
"""
    return md

# ---------------- Email / Scheduler ----------------
def send_or_schedule(config, md_text, user_email):
    html_text = convert_md_to_html(md_text)
    sender = os.getenv("DEFAULT_FROM_NAME","Social Intelligence Agent")
    subj = f"{config['brand']['name']} Social Media Report"
    choice = ai_input("Do you want to send the email now or schedule every 48 hours? (1=Now, 2=Schedule)")
    if choice == "1":
        send_email(config["gmail"]["client_secret_file"], config["gmail"]["token_file"], sender, [user_email, config["brand"]["team_email"]], subj, html_text, is_html=True)
        print("\n✅ Email Sent Successfully!\n")
    elif choice == "2":
        hours = 48
        schedule_every(lambda: send_email(config["gmail"]["client_secret_file"], config["gmail"]["token_file"], sender, [user_email, config["brand"]["team_email"]], subj, html_text, is_html=True), hours)
        print(f"⏱️ Scheduled to run every {hours} hours.\n")
    else:
        print("⚠️ Invalid choice, skipping email.\n")

# ---------------- Main Workflow ----------------
def main():
    with open(CONFIG_PATH,"r",encoding="utf-8") as f:
        config = yaml.safe_load(f)

    while True:
        print("\n=== AI Social Media Intelligence Agent ===\n")

        greeting = get_ai_message("Greet the user and explain your purpose as Social Media Intelligence Agent.")

        # --- Collect User Info ---
        name = ai_input("What is your name?")
        company = ai_input("Which company do you represent?")
        email = ai_input("What is your email address?")
        user_data = {"name": name, "company": company, "email": email}

        # --- File Upload ---
        while True:
            file_path = ai_input("Please provide the DOCX/CSV file path containing social media handles.")
            if os.path.exists(file_path):
                break
            print("⚠️ File not found. Please provide a valid path.\n")
        user_data["file_path"] = file_path

        # --- Proceed Confirmation ---
        proceed = ai_input("Do you want to proceed with analysis? (y/n)")
        if proceed.lower() != "y":
            farewell = get_ai_message("Say goodbye politely.")
            break

        # --- Parse handles ---
        accounts = parse_handles_from_docx(file_path) if file_path.lower().endswith(".docx") else parse_handles_from_csv(file_path)
        accounts = [i for i in accounts if i["platform"].lower() in ("youtube","instagram","linkedin")]

        # --- Lookback ---
        lookback_hours = int(config.get("analysis",{}).get("lookback_hours",48))
        user_data["lookback_hours"] = lookback_hours

        # --- Fetch Content ---
        items = fetch_social_content(accounts, lookback_hours)

        # --- AI Analysis ---
        analysis_results = analyze_content_with_ollama(items)

        # --- Build Report ---
        md_report = build_md_report(user_data, analysis_results)
        save_report(md_report, "data/reports")

        # --- Email / Schedule ---
        send_or_schedule(config, md_report, email)

        # --- Ask to Analyze Again ---
        again = ai_input("Do you want to analyze another set? (y/n)")
        if again.lower() != "y":
            farewell = get_ai_message("Say goodbye politely.")
            break

if __name__ == "__main__":
    main()