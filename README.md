# 📞 CallSense — Multilingual Call Sentiment & Best-Time Predictor

> Built as an open-source project inspired by the real challenges Indian contact centers face — particularly around multilingual customer communication and low pickup rates.

---

## 🎯 Problem This Solves

Indian contact centers (BFSI, Telecom, E-commerce) face two big problems:

1. **60%+ outbound calls go unanswered** — wrong timing, spam perception, or customer unavailability
2. **Multilingual sentiment analysis is mostly manual** — agents can't quickly gauge if a Hindi/Marathi/English customer is cooperative or about to file a complaint

CallSense automates both.

---

## ✨ Features

| Feature | What it does |
|---|---|
| 🌐 Multilingual Sentiment | Detects sentiment in Hindi, Marathi, English — no translation needed |
| ⏰ Best-Time Predictor | Recommends the best hour + day to call based on customer history |
| 📝 Auto Call Summary | Generates 2-3 line summary + action items after each call |
| 📊 Live Dashboard | Streamlit dashboard with emotion breakdown, pickup probability, call insights |

---

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/callsense.git
cd callsense

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Add Claude API key for smart summaries
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# 4. Test the modules
python modules/sentiment_analyzer.py
python modules/time_predictor.py
python modules/call_summarizer.py

# 5. Launch dashboard
streamlit run dashboard/app.py
```

---

## 📁 Project Structure

```
callsense/
├── modules/
│   ├── sentiment_analyzer.py   # Hindi/Marathi/English sentiment detection
│   ├── time_predictor.py       # Best call time recommendation engine
│   └── call_summarizer.py      # Auto summary + action items (Claude API)
├── dashboard/
│   └── app.py                  # Streamlit dashboard
├── data/sample/
│   └── sample_calls.json       # Sample multilingual call transcripts
└── requirements.txt
```

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **Transformers / IndicBERT** — Multilingual NLP
- **scikit-learn** — Pickup time prediction model
- **Claude API (Anthropic)** — Intelligent call summarization
- **Streamlit + Plotly** — Interactive dashboard
- **Whisper** — Speech-to-text (for actual audio files)

---

## 🔮 What's Next

- [ ] Integrate with real Whisper transcription pipeline
- [ ] Train on actual labeled call center data
- [ ] Add WhatsApp sentiment tracking
- [ ] REST API wrapper for easy integration

---

## 🙏 Inspiration

This project was inspired by the work **Saarthi.ai** is doing in multilingual conversational AI for Indian contact centers. Their product [Pravid.io](https://pravid.io) solves enterprise-scale communication challenges — this is a small open-source exploration of some underlying problems.

---

## 👨‍💻 Author

Built by Aditya karjule — Pune, India 🇮🇳  
Open to feedback, collaborations, and conversations!

LinkedIn: www.linkedin.com/in/aditya-karjule-38427925a  
GitHub: https://github.com/Aditya-karjule
