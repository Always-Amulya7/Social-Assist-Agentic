# 📊 Social Media Intelligence Agent

An **AI-powered social media intelligence tool** that collects recent posts from YouTube, Instagram, and LinkedIn, analyzes them with `gpt-oss` (via [Ollama](https://ollama.ai)), and generates **professional summary reports**.  
Reports are automatically **emailed** to your inbox or **scheduled** to run periodically.  

---

## ✨ Features

- 🔎 Collects posts from **YouTube, Instagram, and LinkedIn**  
- 🤖 **AI-powered summaries** using `gpt-oss:20b` for professional insights  
- 📈 **Trend & sentiment analysis** of fetched content  
- 📧 **Email reporting** via Gmail API  
- ⏱ **Scheduling support** (e.g., auto-generate every 48h)  
- 📂 **Report storage** in Markdown & HTML formats  

---

## 🛠️ Requirements

- **Python 3.9+**  
- [Ollama](https://ollama.ai) installed locally with gpt-oss:20b  
- Gmail API credentials (for sending reports)  
- Internet access (to fetch content & AI summaries)  

---

## ⚙️ Installation

```bash
# Clone the repo
git clone https://github.com/your-username/social-intelligence-agent.git
cd social-intelligence-agent

# Create a virtual environment
python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt

# Install Ollama & pull the model
ollama pull gpt-oss:20b

```

---

## 📄 Configuration

- Copy `config.example.yaml` to `config.yaml`:
  
  ```bash
  cp config.example.yaml config.yaml
  ```
- Update the repo with:
  - In the credential folder paste you OAuth json credentials file ie Gmail credentials (`client_secret.json`, `token.json`) 
  - Brand name & team email  
  - Reporting schedule (`lookback_hours`, etc.)  

---

## 🚀 Running the Agent

```bash
python app.py
```

### Example Flow
1. You’ll be greeted by the AI assistant.  
2. Enter your **name, company, and email**.  
3. Provide a **DOCX/CSV file** with account handles (YouTube, Instagram, LinkedIn).  
4. The AI will:  
   - Fetch recent content  
   - Summarize it with GPT-OSS  
   - Generate a structured intelligence report  
5. You can **send the report immediately** or **schedule it** to run automatically.  

---

## 📧 Email Reports

- Reports are sent to **your email** and your **team’s email** (from `config.yaml`).  
- Format: **HTML email** with executive summary + detailed breakdown.  
- Reports are also saved under `/data/reports/`.  

---

## 📂 Project Structure

```
Social Assist Agentic
├── app.py                       # Main application
├── config.yaml / config.example.yaml
├── utils/                       # Parsers, scheduler, helpers
├── collectors/                  # YouTube, Instagram, LinkedIn scrapers
├── analysis/                    # AI analysis logic
├── reporting/                   # Report builder + email sender
├── data/reports/                # Saved reports
├── requirements.txt
└── README.md
```

---

## 🔮 Future Improvements

- 📱 Support Twitter/X, TikTok, and Facebook  
- 🌐 Web dashboard for report browsing  
- ☁️ Cloud deployment with persistent scheduling to be permanently

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to change.  

---

## 📜 License

[MIT](LICENSE) © Amulya Shrivastava
