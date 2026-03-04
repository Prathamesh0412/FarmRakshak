"""
yield_estimator.py - Financial Yield Loss Calculator
Converts lodging severity into Rupee loss estimates using
India's Minimum Support Price (MSP) data per crop type.

MSP Reference: CACP (Commission for Agricultural Costs and Prices)
Kharif 2024-25 MSP rates from Government of India.
"""

from typing import Dict, Tuple


# ── MSP Data (per quintal, Kharif 2024-25, GOI rates) ─────────────────────────
# Source: Cabinet Committee on Economic Affairs (CCEA) announcements
MSP_PER_QUINTAL = {
    "wheat":       2275,   # Rabi 2024-25
    "rice":        2300,   # Kharif 2024-25
    "maize":       2090,
    "sorghum":     3371,   # Jowar
    "bajra":       2625,   # Pearl millet
    "sugarcane":   340,    # Per quintal (Fair & Remunerative Price)
    "cotton":      7121,   # Medium staple
    "soybean":     4892,
    "groundnut":   6783,
    "sunflower":   7280,
    "tur_dal":     7550,   # Arhar/Pigeon pea
    "moong":       8682,
    "urad":        7400,
}

# Average yield per acre (quintals) for each crop under normal conditions
# Based on Indian Council of Agricultural Research (ICAR) averages
YIELD_PER_ACRE = {
    "wheat":       16.0,
    "rice":        18.0,
    "maize":       14.0,
    "sorghum":     9.0,
    "bajra":       8.0,
    "sugarcane":   300.0,   # Much higher yield
    "cotton":      7.5,
    "soybean":     10.0,
    "groundnut":   12.0,
    "sunflower":   8.0,
    "tur_dal":     6.0,
    "moong":       5.0,
    "urad":        5.0,
}

# Lodging severity → actual yield loss percentage range
# Based on published agronomical research
LODGING_LOSS_FACTOR = {
    "healthy":  (0.0,   0.0),   # No loss
    "mild":     (0.05,  0.15),  # 5-15% loss
    "moderate": (0.20,  0.40),  # 20-40% loss
    "severe":   (0.45,  0.80),  # 45-80% loss
}

# Human-readable crop display names (English + bilingual)
CROP_DISPLAY = {
    "wheat":       "Wheat (Gehun / \u0917\u0947\u0939\u0942\u0902)",
    "rice":        "Rice (Dhan / \u0927\u093e\u0928)",
    "maize":       "Maize (Makka / \u092e\u0915\u094d\u0915\u093e)",
    "sorghum":     "Sorghum (Jowar / \u091c\u094d\u0935\u093e\u0930\u0940)",
    "bajra":       "Bajra (Pearl Millet / \u092c\u093e\u091c\u0930\u093e)",
    "sugarcane":   "Sugarcane (Ganna / \u0909\u0938 )",
    "cotton":      "Cotton (Kapas / \u0915\u092a\u093e\u0938)",
    "soybean":     "Soybean (Soya / \u0938\u094b\u092f\u093e)",
    "groundnut":   "Groundnut (Moongfali / \u092e\u0942\u0902\u0917\u092b\u0932\u0940)",
    "sunflower":   "Sunflower (Surajmukhi / \u0938\u0942\u0930\u091c\u092e\u0941\u0916\u0940)",
    "tur_dal":     "Tur/Arhar Dal",
    "moong":       "Moong Dal (Green Gram)",
    "urad":        "Urad Dal (Black Gram)",
}


def estimate_loss(
    crop: str,
    severity_class: str,
    acres: float
) -> Dict:
    """
    Estimates financial yield loss in Indian Rupees.

    Args:
        crop:           Crop key from CROP_DISPLAY
        severity_class: Predicted class (healthy/mild/moderate/severe)
        acres:          Field area in acres

    Returns:
        Dict with:
            - expected_yield_qtl   Total yield without lodging (quintals)
            - loss_low_qtl         Lower loss estimate (quintals)
            - loss_high_qtl        Upper loss estimate (quintals)
            - loss_low_inr         Lower loss in rupees
            - loss_high_inr        Upper loss in rupees
            - gross_value_inr      Total crop value without damage
            - loss_pct_low         Low percentage
            - loss_pct_high        High percentage
            - msp_per_qtl          Current MSP
    """
    msp = MSP_PER_QUINTAL.get(crop, 2000)
    yield_qtl_per_acre = YIELD_PER_ACRE.get(crop, 12.0)
    loss_low_pct, loss_high_pct = LODGING_LOSS_FACTOR.get(severity_class, (0.0, 0.0))

    total_yield   = yield_qtl_per_acre * acres
    gross_value   = total_yield * msp
    loss_low_qtl  = total_yield * loss_low_pct
    loss_high_qtl = total_yield * loss_high_pct
    loss_low_inr  = loss_low_qtl * msp
    loss_high_inr = loss_high_qtl * msp

    return {
        "crop":              CROP_DISPLAY.get(crop, crop.title()),
        "crop_key":          crop,
        "acres":             acres,
        "msp_per_qtl":       msp,
        "expected_yield_qtl": round(total_yield, 2),
        "gross_value_inr":   round(gross_value, 0),
        "loss_low_qtl":      round(loss_low_qtl, 2),
        "loss_high_qtl":     round(loss_high_qtl, 2),
        "loss_low_inr":      round(loss_low_inr, 0),
        "loss_high_inr":     round(loss_high_inr, 0),
        "loss_pct_low":      round(loss_low_pct * 100, 0),
        "loss_pct_high":     round(loss_high_pct * 100, 0),
        "severity_class":    severity_class,
    }


def format_inr(amount: float) -> str:
    """Formats a number in Indian currency style (lakhs/thousands)."""
    if amount >= 100000:
        return f"\u20b9{amount/100000:.1f} Lakh"
    elif amount >= 1000:
        return f"\u20b9{amount:,.0f}"
    else:
        return f"\u20b9{amount:.0f}"
