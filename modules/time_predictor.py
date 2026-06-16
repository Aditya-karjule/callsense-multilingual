"""
CallSense - Best Time to Call Predictor
Predicts the best hour to call a customer based on:
- Day of week
- Previous unanswered calls
- Language/region patterns
- Historical pickup patterns
"""

import json
import random
from dataclasses import dataclass


@dataclass
class TimeRecommendation:
    best_hour: int
    best_day: str
    confidence: float       # 0.0 to 1.0
    reason: str
    avoid_hours: list
    pickup_probability: float


# Known pickup patterns for Indian contact centers (research-based)
PICKUP_PATTERNS = {
    "peak_hours": [10, 11, 17, 18, 19],        # Best pickup times in India
    "low_hours":  [8, 9, 13, 14, 22, 23],       # Bad times (commute / lunch / late)
    "best_days":  ["Tuesday", "Wednesday", "Thursday"],
    "avoid_days": ["Monday", "Friday", "Saturday", "Sunday"]
}

# Language-based regional adjustments
REGIONAL_PATTERNS = {
    "hindi":   {"peak_shift": 0,  "lunch_break": 13},   # North India
    "marathi": {"peak_shift": 0,  "lunch_break": 13},   # Pune/Mumbai
    "english": {"peak_shift": -1, "lunch_break": 14},   # Corporate users
}


def predict_best_time(
    previous_unanswered: int,
    language: str = "hindi",
    last_call_hour: int = None,
    last_call_day: str = None
) -> TimeRecommendation:
    """
    Predict the best time to call a customer.

    Args:
        previous_unanswered : Number of previous unanswered calls
        language            : Customer's preferred language
        last_call_hour      : Hour of last attempted call (0-23)
        last_call_day       : Day of last attempted call

    Returns:
        TimeRecommendation with best time, confidence, and reasoning
    """
    pattern = REGIONAL_PATTERNS.get(language, REGIONAL_PATTERNS["hindi"])
    peak = PICKUP_PATTERNS["peak_hours"].copy()

    # If last call was at a peak hour and went unanswered, try a different one
    if last_call_hour and last_call_hour in peak:
        peak = [h for h in peak if h != last_call_hour]

    # Shift peak based on region
    best_hour = (peak[0] + pattern["peak_shift"]) % 24

    # Avoid the lunch hour for this region
    lunch = pattern["lunch_break"]
    avoid = PICKUP_PATTERNS["low_hours"] + [lunch]

    # More unanswered calls → lower confidence, try evening slots
    if previous_unanswered >= 5:
        best_hour = 18       # Evening — higher chance after work
        confidence = 0.45
        reason = f"Customer ne {previous_unanswered} calls miss kiye — evening slot try karo (6 PM)"
    elif previous_unanswered >= 2:
        best_hour = 17
        confidence = 0.60
        reason = f"{previous_unanswered} missed calls — late afternoon try karo (5 PM)"
    else:
        confidence = 0.78
        reason = "Fresh customer — morning peak hour best rahega (10-11 AM)"

    # Pick best day (avoid last call's day if possible)
    best_days = PICKUP_PATTERNS["best_days"].copy()
    if last_call_day in best_days:
        best_days = [d for d in best_days if d != last_call_day]
    best_day = best_days[0] if best_days else "Wednesday"

    # Pickup probability estimate
    base_prob = 0.65
    penalty   = previous_unanswered * 0.05
    pickup_prob = max(0.15, round(base_prob - penalty, 2))

    return TimeRecommendation(
        best_hour=best_hour,
        best_day=best_day,
        confidence=confidence,
        reason=reason,
        avoid_hours=avoid[:5],
        pickup_probability=pickup_prob
    )


def format_hour(hour: int) -> str:
    """Convert 24h to readable 12h format."""
    if hour == 0:
        return "12:00 AM"
    elif hour < 12:
        return f"{hour}:00 AM"
    elif hour == 12:
        return "12:00 PM"
    else:
        return f"{hour - 12}:00 PM"


def batch_predict(calls: list) -> list:
    """Generate time recommendations for a list of calls."""
    results = []
    for call in calls:
        rec = predict_best_time(
            previous_unanswered=call.get("previous_calls_unanswered", 0),
            language=call.get("language", "hindi"),
            last_call_hour=call.get("hour"),
            last_call_day=call.get("day_of_week")
        )
        results.append({
            "call_id": call.get("call_id", "N/A"),
            "customer_name": call.get("customer_name", "Unknown"),
            "best_time": format_hour(rec.best_hour),
            "best_day": rec.best_day,
            "pickup_probability": f"{int(rec.pickup_probability * 100)}%",
            "confidence": f"{int(rec.confidence * 100)}%",
            "reason": rec.reason,
            "avoid_hours": [format_hour(h) for h in rec.avoid_hours]
        })
    return results


# ── Quick test ──────────────────────────────────────────────
if __name__ == "__main__":
    test_cases = [
        {"name": "Ramesh (2 missed, Hindi)",   "unanswered": 2, "lang": "hindi",   "hour": 10, "day": "Monday"},
        {"name": "Priya (0 missed, Marathi)",  "unanswered": 0, "lang": "marathi", "hour": 14, "day": "Tuesday"},
        {"name": "Amit (8 missed, Hindi)",     "unanswered": 8, "lang": "hindi",   "hour": 8,  "day": "Tuesday"},
        {"name": "Sunita (0 missed, English)", "unanswered": 0, "lang": "english", "hour": 12, "day": "Wednesday"},
    ]

    print("=" * 55)
    print("CallSense — Best Time Predictor Test")
    print("=" * 55)
    for case in test_cases:
        rec = predict_best_time(
            previous_unanswered=case["unanswered"],
            language=case["lang"],
            last_call_hour=case["hour"],
            last_call_day=case["day"]
        )
        print(f"\nCustomer : {case['name']}")
        print(f"Best Time: {format_hour(rec.best_hour)} on {rec.best_day}")
        print(f"Pickup % : {int(rec.pickup_probability * 100)}%")
        print(f"Reason   : {rec.reason}")
        print(f"Avoid    : {[format_hour(h) for h in rec.avoid_hours]}")
