"""
CallSense - Auto Call Summarizer
Uses Claude API to generate:
- Short call summary (2-3 lines)
- Customer intent
- Action items for the agent
- Next step recommendation
"""

import os
import json

try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False


SYSTEM_PROMPT = """You are a contact center AI assistant for an Indian financial services company.
Analyze the given call transcript and return ONLY a JSON object with these keys:
- summary: 2-3 line summary of the call in simple English
- customer_intent: one of [promise_to_pay, already_paid, needs_info, angry_refused, callback_requested, other]
- sentiment: one of [positive, negative, neutral]
- action_items: list of 1-3 concrete next steps for the agent
- next_call_suggestion: when to follow up (e.g., "Call after 3 days", "Do not call - escalate")
- priority: one of [high, medium, low]

Return ONLY valid JSON. No markdown, no explanation."""


def summarize_call(transcript: str, call_id: str = "N/A") -> dict:
    """
    Summarize a call transcript using Claude API.
    Falls back to rule-based summary if API not available.
    
    Args:
        transcript : The call transcript text
        call_id    : Optional call ID for reference
    
    Returns:
        dict with summary, intent, action_items, next_call_suggestion, priority
    """
    if CLAUDE_AVAILABLE and os.getenv("ANTHROPIC_API_KEY"):
        return _summarize_with_claude(transcript, call_id)
    else:
        return _summarize_rule_based(transcript, call_id)


def _summarize_with_claude(transcript: str, call_id: str) -> dict:
    """Use Claude API for smart summarization."""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Call ID: {call_id}\n\nTranscript:\n{transcript}"
            }
        ]
    )

    raw = message.content[0].text.strip()
    # Clean any accidental markdown
    raw = raw.replace("```json", "").replace("```", "").strip()
    result = json.loads(raw)
    result["call_id"] = call_id
    result["source"] = "claude-api"
    return result


def _summarize_rule_based(transcript: str, call_id: str) -> dict:
    """
    Fallback rule-based summarizer (no API needed).
    Good enough for demo purposes.
    """
    text = transcript.lower()

    # Detect intent
    if any(w in text for w in ["payment kar", "bhej dunga", "will pay", "settle", "kartoy"]):
        intent = "promise_to_pay"
        priority = "medium"
        action = ["Log promise to pay", "Schedule follow-up in 3 days", "Send WhatsApp reminder"]
        next_call = "Follow up after 3 days"
        sentiment = "positive"
        summary = "Customer acknowledged the due amount and promised to make payment soon."

    elif any(w in text for w in ["already paid", "kelay", "paid", "kar chuka"]):
        intent = "already_paid"
        priority = "low"
        action = ["Verify payment in system", "Update customer record", "Close ticket if confirmed"]
        next_call = "Verify payment first before next call"
        sentiment = "neutral"
        summary = "Customer claims payment has already been made. Needs verification."

    elif any(w in text for w in ["complaint", "remove", "spam", "stop", "nako", "mat karo"]):
        intent = "angry_refused"
        priority = "high"
        action = ["Mark DND if requested", "Escalate to supervisor", "Review call count for this customer"]
        next_call = "Do not call - review DND status first"
        sentiment = "negative"
        summary = "Customer is angry and refused to engage. Possible spam complaint or excessive calling."

    else:
        intent = "needs_info"
        priority = "medium"
        action = ["Send detailed payment breakdown", "Follow up in 2 days", "Offer alternate payment options"]
        next_call = "Call again in 2 days with payment details ready"
        sentiment = "neutral"
        summary = "Customer requested more information. Agent should prepare detailed breakdown before next call."

    return {
        "call_id": call_id,
        "summary": summary,
        "customer_intent": intent,
        "sentiment": sentiment,
        "action_items": action,
        "next_call_suggestion": next_call,
        "priority": priority,
        "source": "rule-based"
    }


def batch_summarize(calls: list) -> list:
    """Summarize a list of calls."""
    return [
        summarize_call(call["transcript"], call.get("call_id", "N/A"))
        for call in calls
    ]


# ── Quick test ──────────────────────────────────────────────
if __name__ == "__main__":
    test_transcripts = [
        ("C001", "Haan theek hai, kal tak payment kar dunga pakka. Account number bata do."),
        ("C002", "Mala aadhee saang, mi payment kelay last week already."),
        ("C003", "Stop calling me! This is spam! I will file a complaint!"),
    ]

    print("=" * 55)
    print("CallSense — Call Summarizer Test")
    print("=" * 55)
    for call_id, transcript in test_transcripts:
        result = summarize_call(transcript, call_id)
        print(f"\nCall ID : {result['call_id']}")
        print(f"Summary : {result['summary']}")
        print(f"Intent  : {result['customer_intent']}")
        print(f"Priority: {result['priority']}")
        print(f"Actions : {result['action_items']}")
        print(f"Next    : {result['next_call_suggestion']}")
        print(f"Source  : {result['source']}")
