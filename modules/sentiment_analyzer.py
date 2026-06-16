"""
CallSense - Multilingual Sentiment Analyzer
Supports: Hindi, Marathi, English
Uses: Rule-based + keyword approach (no heavy model download needed for demo)
For production: swap with ai4bharat/indic-bert
"""

from dataclasses import dataclass


@dataclass
class SentimentResult:
    label: str          # positive / negative / neutral
    score: float        # 0.0 to 1.0
    emotion: str        # angry / cooperative / frustrated / neutral / satisfied
    language: str
    key_phrases: list


# Keyword banks per language
KEYWORDS = {
    "hindi": {
        "positive": ["theek", "haan", "zaroor", "kar dunga", "kar dungi", "bhej dunga",
                     "payment", "samajh", "shukriya", "pakka", "bilkul"],
        "negative": ["nahi", "mat karo", "spam", "complaint", "gussa", "band karo",
                     "pareshan", "phone mat", "remove", "dikkat"],
        "angry":   ["complaint karunga", "spam", "phone mat karo", "remove karo",
                    "court", "police", "mat karo"],
        "cooperative": ["theek hai", "kar dunga", "bhej dunga", "samajh gaya",
                        "kal tak", "pakka", "zaroor"]
    },
    "marathi": {
        "positive": ["theek", "haan", "kartoy", "kelay", "saang", "dhanyavad"],
        "negative": ["nako", "band kara", "complaint", "trasdata", "phone nako"],
        "angry":   ["complaint", "nako", "band kara"],
        "cooperative": ["kartoy", "saangtoy", "kelay", "payment"]
    },
    "english": {
        "positive": ["thank", "yes", "sure", "will pay", "settle", "okay", "understand",
                     "breakdown", "end of month", "appreciate"],
        "negative": ["not interested", "remove", "stop calling", "spam", "complaint",
                     "do not call", "annoying", "harassing"],
        "angry":   ["stop calling", "remove my number", "complaint", "harassing",
                    "do not call", "not interested"],
        "cooperative": ["will pay", "settle", "thank", "yes", "understand", "okay"]
    }
}


def detect_language(text: str) -> str:
    """Detect language from Devanagari script OR Romanized Hindi/Marathi."""
    # Check actual Devanagari script first
    devanagari_chars = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    if devanagari_chars > 3:
        marathi_markers = ["मला", "तुम्ही", "करतोय"]
        if any(m in text for m in marathi_markers):
            return "marathi"
        return "hindi"

    # Romanized detection
    text_lower = text.lower()
    marathi_markers = ["mala", "tumhi", "kunakaduun", "kartoy", "saangtoy",
                       "aadhee", "saang", "kelay", "nako"]
    hindi_markers   = ["haan", "theek", "karo", "dunga", "dungi", "karunga",
                       "pakka", "bhai", "mat karo", "nahi", "abhi", "bhej",
                       "paisa", "zaroor", "bilkul", "kar dunga"]

    marathi_score = sum(1 for m in marathi_markers if m in text_lower)
    hindi_score   = sum(1 for m in hindi_markers   if m in text_lower)

    if marathi_score > hindi_score:
        return "marathi"
    elif hindi_score > 0:
        return "hindi"
    return "english"


def analyze_sentiment(transcript: str, language: str = None) -> SentimentResult:
    """
    Analyze sentiment of a call transcript.
    
    Args:
        transcript: The call transcript text
        language: 'hindi', 'marathi', 'english' or None (auto-detect)
    
    Returns:
        SentimentResult with label, score, emotion, language, key_phrases
    """
    if not language:
        language = detect_language(transcript)

    text_lower = transcript.lower()
    kw = KEYWORDS.get(language, KEYWORDS["english"])

    # Count keyword matches
    pos_matches = [w for w in kw["positive"] if w in text_lower]
    neg_matches = [w for w in kw["negative"] if w in text_lower]
    angry_matches = [w for w in kw["angry"] if w in text_lower]
    coop_matches  = [w for w in kw["cooperative"] if w in text_lower]

    pos_score = len(pos_matches)
    neg_score = len(neg_matches)

    # Determine sentiment label
    if pos_score > neg_score:
        label = "positive"
        score = min(0.5 + (pos_score - neg_score) * 0.1, 0.99)
    elif neg_score > pos_score:
        label = "negative"
        score = min(0.5 + (neg_score - pos_score) * 0.1, 0.99)
    else:
        label = "neutral"
        score = 0.5

    # Determine emotion
    if angry_matches:
        emotion = "angry"
    elif coop_matches:
        emotion = "cooperative"
    elif label == "negative":
        emotion = "frustrated"
    elif label == "positive":
        emotion = "satisfied"
    else:
        emotion = "neutral"

    key_phrases = list(set(pos_matches + neg_matches))[:5]

    return SentimentResult(
        label=label,
        score=round(score, 2),
        emotion=emotion,
        language=language,
        key_phrases=key_phrases
    )


def batch_analyze(calls: list) -> list:
    """Analyze a list of call dicts (each must have 'transcript' key)."""
    results = []
    for call in calls:
        lang = call.get("language")
        result = analyze_sentiment(call["transcript"], lang)
        results.append({
            "call_id": call.get("call_id", "N/A"),
            "customer_name": call.get("customer_name", "Unknown"),
            "sentiment": result.label,
            "sentiment_score": result.score,
            "emotion": result.emotion,
            "language": result.language,
            "key_phrases": result.key_phrases,
            "outcome": call.get("outcome", "unknown")
        })
    return results


# ── Quick test ──────────────────────────────────────────────
if __name__ == "__main__":
    test_cases = [
        ("Haan theek hai, kal tak payment kar dunga pakka.", None),
        ("Phone mat karo mujhe! Spam hai yeh, complaint karunga!", None),
        ("I will settle the amount by end of month, thank you.", "english"),
        ("Mala aadhee saang, mi payment kelay last week.", None),
    ]

    print("=" * 55)
    print("CallSense — Sentiment Analyzer Test")
    print("=" * 55)
    for transcript, lang in test_cases:
        result = analyze_sentiment(transcript, lang)
        emoji = {"positive": "✅", "negative": "❌", "neutral": "➖"}[result.label]
        print(f"\nText    : {transcript[:55]}...")
        print(f"Language: {result.language}")
        print(f"Sentiment: {emoji} {result.label.upper()} ({result.score})")
        print(f"Emotion : {result.emotion}")
        print(f"Keywords: {result.key_phrases}")
