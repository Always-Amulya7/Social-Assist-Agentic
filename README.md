# Social Media Intelligence Agent

An autonomous agent for brand teams that monitors **YouTube, Instagram, and LinkedIn** accounts from a provided list and sends a concise **trend brief every 48 hours**.

## Features
- Guided CLI “agent” flow (greeting → collect name/company/email → Gmail auth → upload list → analysis → schedule)
- Pulls content from:
  - **YouTube** (no API key required via RSS; API key optional)
  - **Instagram** (via `instaloader` for public profiles)
  - **LinkedIn** (via Apify actor API or placeholder; see config)
- NLP pipeline:
  - Summarization (LexRank)
  - Keyword extraction (YAKE)
  - Sentiment analysis (VADER)
- Trend detection across accounts and platforms; compares against last report
- Report generation to Markdown + email via **Gmail OAuth** (no app password needed)
- Automated scheduling every **48 hours** (APScheduler) or immediate send

## Quick Start
1. **Install** Python 3.10+ and run:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   - Copy `.env.example` to `.env` and fill values (optional keys).
   - Copy `config.example.yaml` to `config.yaml` and adjust (e.g., schedule hour, timezone).

3. **Gmail OAuth setup**:
   - Create a Google Cloud project → Enable **Gmail API**.
   - Create OAuth 2.0 Client ID (Desktop App).
   - Download `credentials.json` and place it in `credentials/`.
   - First send will trigger a browser OAuth flow and create `credentials/token.json`.

4. **Prepare account list**:
   - Provide a **DOCX** or **CSV** with one handle/URL per line (or a two-column table with `platform, handle`).
   - Example in `data/sample_influencers.csv`.

5. **Run agent**:
   ```bash
   python app.py
   ```
   The agent walks you through greeting → Gmail auth → document upload → analysis → scheduling.

## Supported Inputs
- **YouTube**: `channel_id`, full channel URL, or vanity URL. (RSS used if no API key.)
- **Instagram**: public usernames. (Private accounts require login; see notes in `collectors/instagram_collector.py`.)
- **LinkedIn**: company or person profile URLs (requires `APIFY_TOKEN` to enable scraping via actor).

## Outputs
- Trend brief Markdown saved to `data/reports/YYYY-MM-DD_HHMM_trend_brief.md`.
- Email sent via Gmail to the collected email and/or distribution list from `config.yaml`.

## Scheduling
- Default: every **48 hours** from the time you select "Schedule every 48 hours".
- Uses persistent job store in `data/schedule.json` to remember last run.

## Security & Notes
- Tokens live in `credentials/token.json` (gitignore suggested).
- Be mindful of each platform's Terms of Service; prefer official APIs when available.
- This project is provided under the MIT License; see `LICENSE`.

