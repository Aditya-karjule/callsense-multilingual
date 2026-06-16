"""
CallSense — Streamlit Dashboard
Run: streamlit run dashboard/app.py
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from modules.sentiment_analyzer import batch_analyze
from modules.time_predictor import batch_predict
from modules.call_summarizer import summarize_call

# ── Page config ─────────────────────────────────────────────
st.set_page_config(
    page_title="CallSense | Multilingual Call AI",
    page_icon="📞",
    layout="wide"
)

# ── Custom CSS ───────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f172a; }
    .metric-card {
        background: #1e293b;
        border-radius: 12px;
        padding: 16px 20px;
        border-left: 4px solid #6366f1;
    }
    .stMetric label { color: #94a3b8 !important; font-size: 0.8rem !important; }
    .stMetric .metric-value { color: #f1f5f9 !important; }
    h1, h2, h3 { color: #f1f5f9 !important; }
    .emotion-angry    { color: #ef4444; font-weight: bold; }
    .emotion-coop     { color: #22c55e; font-weight: bold; }
    .emotion-neutral  { color: #94a3b8; }
    .emotion-frustrated { color: #f97316; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────
st.markdown("## 📞 CallSense")
st.markdown("**Multilingual Call Sentiment & Best-Time Predictor** | Built for Saarthi.ai's use case")
st.divider()

# ── Load sample data ─────────────────────────────────────────
@st.cache_data
def load_data():
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample", "sample_calls.json")
    with open(data_path) as f:
        return json.load(f)

calls = load_data()

# ── Sidebar: Add custom call ─────────────────────────────────
with st.sidebar:
    st.markdown("### ➕ Test Custom Call")
    custom_transcript = st.text_area(
        "Paste call transcript",
        placeholder="Haan theek hai, kal tak payment kar dunga...",
        height=120
    )
    custom_lang = st.selectbox("Language", ["hindi", "marathi", "english"])
    custom_unanswered = st.slider("Previous unanswered calls", 0, 10, 0)

    if st.button("🔍 Analyze", use_container_width=True):
        if custom_transcript.strip():
            from modules.sentiment_analyzer import analyze_sentiment
            from modules.time_predictor import predict_best_time, format_hour

            sent = analyze_sentiment(custom_transcript, custom_lang)
            time = predict_best_time(custom_unanswered, custom_lang)
            summ = summarize_call(custom_transcript, "CUSTOM")

            st.markdown("---")
            emoji = {"positive": "✅", "negative": "❌", "neutral": "➖"}[sent.label]
            st.markdown(f"**Sentiment:** {emoji} `{sent.label}` ({sent.score})")
            st.markdown(f"**Emotion:** `{sent.emotion}`")
            st.markdown(f"**Best Time:** `{format_hour(time.best_hour)}` on `{time.best_day}`")
            st.markdown(f"**Pickup Prob:** `{int(time.pickup_probability*100)}%`")
            st.markdown(f"**Summary:** {summ['summary']}")
            st.markdown(f"**Priority:** `{summ['priority'].upper()}`")
        else:
            st.warning("Transcript paste karo pehle!")

# ── Run analysis ─────────────────────────────────────────────
sentiment_results = batch_analyze(calls)
time_results      = batch_predict(calls)

sent_df = pd.DataFrame(sentiment_results)
time_df = pd.DataFrame(time_results)

# ── KPI Row ──────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

total = len(calls)
positive = sum(1 for r in sentiment_results if r["sentiment"] == "positive")
negative = sum(1 for r in sentiment_results if r["sentiment"] == "negative")
angry    = sum(1 for r in sentiment_results if r["emotion"] == "angry")

col1.metric("📋 Total Calls",     total)
col2.metric("✅ Cooperative",     positive, f"{int(positive/total*100)}%")
col3.metric("❌ Negative",        negative, f"-{int(negative/total*100)}%")
col4.metric("🔥 Angry Customers", angry,    "Needs attention" if angry > 0 else "Clear")

st.divider()

# ── Charts ───────────────────────────────────────────────────
chart1, chart2 = st.columns(2)

with chart1:
    st.markdown("#### Sentiment Distribution")
    sent_counts = sent_df["sentiment"].value_counts().reset_index()
    sent_counts.columns = ["Sentiment", "Count"]
    colors = {"positive": "#22c55e", "negative": "#ef4444", "neutral": "#94a3b8"}
    fig1 = px.pie(
        sent_counts, names="Sentiment", values="Count",
        color="Sentiment", color_discrete_map=colors,
        hole=0.45
    )
    fig1.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#f1f5f9", showlegend=True,
        margin=dict(t=20, b=20)
    )
    st.plotly_chart(fig1, use_container_width=True)

with chart2:
    st.markdown("#### Emotion Breakdown")
    emo_counts = sent_df["emotion"].value_counts().reset_index()
    emo_counts.columns = ["Emotion", "Count"]
    emo_colors = {
        "angry": "#ef4444", "cooperative": "#22c55e",
        "frustrated": "#f97316", "neutral": "#94a3b8", "satisfied": "#6366f1"
    }
    fig2 = px.bar(
        emo_counts, x="Emotion", y="Count",
        color="Emotion", color_discrete_map=emo_colors
    )
    fig2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#f1f5f9", showlegend=False,
        margin=dict(t=20, b=20), xaxis_title="", yaxis_title="Calls"
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── Call Details Table ───────────────────────────────────────
st.markdown("#### 📋 Call-wise Analysis")

merged = pd.merge(
    sent_df[["call_id", "customer_name", "sentiment", "sentiment_score", "emotion", "language", "key_phrases"]],
    time_df[["call_id", "best_time", "best_day", "pickup_probability", "reason"]],
    on="call_id"
)

def color_sentiment(val):
    colors = {"positive": "color: #22c55e", "negative": "color: #ef4444", "neutral": "color: #94a3b8"}
    return colors.get(val, "")

def color_emotion(val):
    colors = {
        "angry": "color: #ef4444; font-weight: bold",
        "cooperative": "color: #22c55e",
        "frustrated": "color: #f97316"
    }
    return colors.get(val, "color: #94a3b8")

styled = merged.style.map(color_sentiment, subset=["sentiment"]) \
                     .map(color_emotion, subset=["emotion"])

st.dataframe(styled, use_container_width=True, hide_index=True)

# ── Best Time Heatmap ────────────────────────────────────────
st.markdown("#### ⏰ Recommended Call Times")
for _, row in time_df.iterrows():
    with st.expander(f"📞 {row['customer_name']} — Best: {row['best_time']} on {row['best_day']} ({row['pickup_probability']} pickup chance)"):
        st.markdown(f"**Reason:** {row['reason']}")
        st.markdown(f"**Confidence:** {row['confidence']}")
        st.markdown(f"**Avoid hours:** {', '.join(row['avoid_hours'])}")

st.divider()
st.markdown(
    "<small>CallSense — Built as an open-source project inspired by Saarthi.ai's multilingual call center challenges. "
    "Not affiliated with Saarthi.ai. | [GitHub](#) | Made in Pune 🇮🇳</small>",
    unsafe_allow_html=True
)
