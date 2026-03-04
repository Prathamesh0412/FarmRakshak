"""
field_history.py - Before/After Field History Tracker
Saves field images with timestamps and metadata for trend comparison.
Uses local filesystem storage (works on both local and HuggingFace Spaces).
"""

import os
import json
import base64
import hashlib
from datetime import datetime
from PIL import Image
from io import BytesIO
from typing import List, Dict, Optional


# ── Storage Directory ─────────────────────────────────────────────────────────
HISTORY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "field_history")
INDEX_FILE  = os.path.join(HISTORY_DIR, "index.json")
MAX_RECORDS = 20  # Keep last 20 snapshots per session to limit disk use


def ensure_dir():
    os.makedirs(HISTORY_DIR, exist_ok=True)


def load_index() -> List[Dict]:
    """Loads the field history index from JSON file."""
    ensure_dir()
    if not os.path.exists(INDEX_FILE):
        return []
    try:
        with open(INDEX_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []


def save_index(records: List[Dict]):
    """Saves the field history index to JSON file."""
    ensure_dir()
    # Keep only last MAX_RECORDS
    records = records[-MAX_RECORDS:]
    with open(INDEX_FILE, "w") as f:
        json.dump(records, f, indent=2)


def save_snapshot(
    pil_image: Image.Image,
    result: Dict,
    crop: str = "unknown",
    acres: float = 1.0,
    farmer_name: str = "",
    field_name: str = ""
) -> str:
    """
    Saves a field snapshot to local storage with prediction metadata.

    Args:
        pil_image:    PIL Image of the field
        result:       Prediction result dict
        crop:         Crop type
        acres:        Field area
        farmer_name:  Optional farmer name
        field_name:   Optional field/plot name

    Returns:
        Snapshot ID string
    """
    ensure_dir()
    timestamp = datetime.now()
    snap_id   = timestamp.strftime("%Y%m%d_%H%M%S")
    img_filename = f"snap_{snap_id}.jpg"
    img_path = os.path.join(HISTORY_DIR, img_filename)

    # Save thumbnail (max 400px) to save disk space
    thumb = pil_image.copy()
    thumb.thumbnail((400, 400), Image.LANCZOS)
    thumb.save(img_path, "JPEG", quality=75)

    # Build record
    record = {
        "id":            snap_id,
        "timestamp":     timestamp.isoformat(),
        "date_display":  timestamp.strftime("%d %b %Y, %I:%M %p"),
        "image_file":    img_filename,
        "predicted_class": result.get("predicted_class", "unknown"),
        "severity_pct":  result.get("severity_pct", 0),
        "confidence":    result.get("confidence", 0),
        "crop":          crop,
        "acres":         acres,
        "farmer_name":   farmer_name,
        "field_name":    field_name,
    }

    # Append to index
    records = load_index()
    records.append(record)
    save_index(records)
    return snap_id


def get_history(limit: int = 10) -> List[Dict]:
    """Returns the most recent N snapshots, newest first."""
    records = load_index()
    return list(reversed(records[-limit:]))


def load_snapshot_image(snap_id: str) -> Optional[Image.Image]:
    """Loads a saved snapshot image by ID."""
    records = load_index()
    for r in records:
        if r["id"] == snap_id:
            img_path = os.path.join(HISTORY_DIR, r["image_file"])
            if os.path.exists(img_path):
                return Image.open(img_path)
    return None


def get_trend(records: List[Dict]) -> str:
    """
    Analyzes trend direction from recent records.
    Returns: improving / worsening / stable / insufficient_data
    """
    if len(records) < 2:
        return "insufficient_data"

    # Compare last two severity scores (newest first from get_history)
    latest = records[0]["severity_pct"]
    prev   = records[1]["severity_pct"]
    delta  = latest - prev

    if delta > 5:
        return "worsening"
    elif delta < -5:
        return "improving"
    else:
        return "stable"


def clear_history():
    """Clears all stored history (for privacy/reset)."""
    records = load_index()
    for r in records:
        img_path = os.path.join(HISTORY_DIR, r.get("image_file", ""))
        if os.path.exists(img_path):
            os.remove(img_path)
    save_index([])


def image_to_base64(pil_image: Image.Image, max_size: int = 200) -> str:
    """Converts PIL image to base64 string for inline HTML display."""
    thumb = pil_image.copy()
    thumb.thumbnail((max_size, max_size), Image.LANCZOS)
    buf = BytesIO()
    thumb.save(buf, format="JPEG", quality=60)
    return base64.b64encode(buf.getvalue()).decode("utf-8")
