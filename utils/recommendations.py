"""
recommendations.py
------------------
Rule-based recommendation engine for FarmRakshak.
Returns localized recommendations based on predicted class + severity.
"""

from typing import Dict


def get_recommendation_key(class_name: str) -> str:
    """
    Returns the translation key for the recommendation message.
    These keys map to the translations JSON files (en/hi/mr).

    Args:
        class_name: One of healthy, mild, moderate, severe

    Returns:
        Translation key string, e.g. rec_mild
    """
    key_map = {
        "healthy":  "rec_healthy",
        "mild":     "rec_mild",
        "moderate": "rec_moderate",
        "severe":   "rec_severe",
    }
    return key_map.get(class_name, "rec_healthy")


def get_urgency_level(class_name: str) -> str:
    """
    Returns a UI urgency tag for the predicted class.
    Used for color coding and priority indicators.
    """
    urgency = {
        "healthy":  "info",
        "mild":     "warning",
        "moderate": "error",
        "severe":   "critical",
    }
    return urgency.get(class_name, "info")


def get_action_timeline(class_name: str) -> str:
    """
    Returns suggested action timeline for each class (English only).
    Used as supplementary information in the UI.
    """
    timelines = {
        "healthy":  "Next check: 7-10 days",
        "mild":     "Next check: 3-5 days",
        "moderate": "Immediate: Within 24-48 hours",
        "severe":   "Emergency: Act today",
    }
    return timelines.get(class_name, "")


def get_yield_impact(class_name: str) -> str:
    """
    Estimated yield impact range for each lodging class.
    Based on agronomical research on crop lodging.
    """
    impacts = {
        "healthy":  "0% — No yield loss expected",
        "mild":     "5-15% — Minor yield reduction possible",
        "moderate": "20-40% — Significant yield loss likely",
        "severe":   "40-80% — Major yield loss. Act immediately",
    }
    return impacts.get(class_name, "Unknown")
