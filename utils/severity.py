"""
severity.py
-----------
Maps model predictions to lodging severity scores.
"""

from typing import Tuple, Dict
import torch

CLASS_NAMES = ["healthy", "mild", "moderate", "severe"]

BASE_SEVERITY = {
    "healthy":  0.0,
    "mild":     15.0,
    "moderate": 35.0,
    "severe":   65.0,
}

SEVERITY_COLORS = {
    "healthy":  "#2ECC71",
    "mild":     "#F39C12",
    "moderate": "#E67E22",
    "severe":   "#E74C3C",
}

SEVERITY_EMOJI = {
    "healthy":  "OK",
    "mild":     "WARN",
    "moderate": "MOD",
    "severe":   "CRIT",
}


def get_severity_score(class_name, confidence):
    """
    Calculates a weighted severity percentage combining the base score
    and confidence of the prediction.
    """
    base = BASE_SEVERITY.get(class_name, 0.0)
    if class_name == "healthy":
        return 0.0
    if confidence >= 0.80:
        return base
    elif confidence >= 0.60:
        return base * (0.85 + 0.15 * confidence)
    else:
        idx = CLASS_NAMES.index(class_name)
        prev_base = BASE_SEVERITY[CLASS_NAMES[max(0, idx - 1)]]
        alpha = confidence
        return prev_base * (1 - alpha) + base * alpha


def get_severity_level(class_name):
    levels = {
        "healthy":  "None",
        "mild":     "Low",
        "moderate": "Medium",
        "severe":   "High",
    }
    return levels.get(class_name, "Unknown")


def parse_model_output(logits):
    """
    Converts raw model logits into structured prediction output.
    Returns: predicted_class, confidence, severity_pct, class_probs
    """
    probs = torch.softmax(logits, dim=1).squeeze(0)
    probs_list = probs.tolist()
    class_probs = {name: round(probs_list[i] * 100, 1)
                   for i, name in enumerate(CLASS_NAMES)}
    top_idx = probs.argmax().item()
    predicted_class = CLASS_NAMES[top_idx]
    confidence = probs_list[top_idx]
    severity_pct = get_severity_score(predicted_class, confidence)
    return predicted_class, confidence, severity_pct, class_probs
