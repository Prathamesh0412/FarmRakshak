"""
pmfby_report.py - PM Fasal Bima Yojana Damage Report Generator
Generates a professional PDF damage assessment report that farmers can
submit as evidence for PMFBY crop insurance claims.

PMFBY = Pradhan Mantri Fasal Bima Yojana (India's national crop insurance program)
This replaces the need for an insurance agent's physical field visit.
"""

from io import BytesIO
from datetime import datetime
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from typing import Dict, Optional


# ── Color Palette ─────────────────────────────────────────────────────────────
GREEN_DARK   = colors.HexColor("#1B5E20")
GREEN_MID    = colors.HexColor("#2E7D32")
GREEN_LIGHT  = colors.HexColor("#A5D6A7")
GREEN_BG     = colors.HexColor("#F1F8E9")
AMBER        = colors.HexColor("#F59E0B")
RED          = colors.HexColor("#DC2626")
ORANGE       = colors.HexColor("#EA580C")
GREY_LIGHT   = colors.HexColor("#F3F4F6")
GREY_DARK    = colors.HexColor("#374151")
GREY_MID     = colors.HexColor("#6B7280")
WHITE        = colors.white
BLACK        = colors.black

SEVERITY_COLORS = {
    "healthy":  colors.HexColor("#10B981"),
    "mild":     colors.HexColor("#F59E0B"),
    "moderate": colors.HexColor("#EA580C"),
    "severe":   colors.HexColor("#DC2626"),
}


def _styles():
    """Returns a dict of custom paragraph styles."""
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "title", parent=base["Title"],
            fontSize=20, textColor=WHITE, alignment=TA_CENTER,
            spaceAfter=2, fontName="Helvetica-Bold"
        ),
        "subtitle": ParagraphStyle(
            "subtitle", parent=base["Normal"],
            fontSize=10, textColor=GREEN_LIGHT, alignment=TA_CENTER,
            spaceAfter=6, fontName="Helvetica"
        ),
        "section_head": ParagraphStyle(
            "section_head", parent=base["Normal"],
            fontSize=11, textColor=WHITE, fontName="Helvetica-Bold",
            leftIndent=6, spaceBefore=4, spaceAfter=4
        ),
        "field_label": ParagraphStyle(
            "field_label", parent=base["Normal"],
            fontSize=9, textColor=GREY_MID, fontName="Helvetica",
            spaceBefore=1
        ),
        "field_value": ParagraphStyle(
            "field_value", parent=base["Normal"],
            fontSize=10, textColor=GREY_DARK, fontName="Helvetica-Bold",
            spaceAfter=4
        ),
        "body": ParagraphStyle(
            "body", parent=base["Normal"],
            fontSize=9.5, textColor=GREY_DARK, fontName="Helvetica",
            leading=14, spaceAfter=4, alignment=TA_JUSTIFY
        ),
        "disclaimer": ParagraphStyle(
            "disclaimer", parent=base["Normal"],
            fontSize=8, textColor=GREY_MID, fontName="Helvetica-Oblique",
            leading=11, spaceAfter=3, alignment=TA_CENTER
        ),
        "verdict": ParagraphStyle(
            "verdict", parent=base["Normal"],
            fontSize=14, fontName="Helvetica-Bold",
            alignment=TA_CENTER, spaceBefore=4, spaceAfter=4
        ),
        "footer": ParagraphStyle(
            "footer", parent=base["Normal"],
            fontSize=7.5, textColor=GREY_MID, fontName="Helvetica",
            alignment=TA_CENTER
        ),
    }


def generate_pmfby_report(
    farmer_name: str,
    village: str,
    district: str,
    state: str,
    crop: str,
    acres: float,
    result: Dict,
    yield_data: Optional[Dict] = None,
    survey_number: str = "",
    policy_number: str = "",
    bank_branch: str = "",
) -> BytesIO:
    """
    Generates a PMFBY-compatible crop damage assessment PDF report.

    Args:
        farmer_name:   Name of the farmer
        village:       Village name
        district:      District name
        state:         State name
        crop:          Crop type (display name)
        acres:         Field area in acres
        result:        Prediction result dict from inference
        yield_data:    Optional yield loss estimate dict
        survey_number: Land survey/khasra number
        policy_number: PMFBY policy number (if available)
        bank_branch:   Lending bank branch (if applicable)

    Returns:
        BytesIO buffer containing the PDF
    """
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=18*mm,
        rightMargin=18*mm,
        topMargin=14*mm,
        bottomMargin=14*mm,
    )

    S = _styles()
    story = []
    pred  = result.get("predicted_class", "unknown")
    sev   = result.get("severity_pct", 0)
    conf  = result.get("confidence", 0)
    sev_color = SEVERITY_COLORS.get(pred, GREY_DARK)

    # ── HEADER BANNER ────────────────────────────────────────────────────────
    header_data = [[
        Paragraph("AGROTILTIX", S["title"]),
        Paragraph("AI Crop Damage Assessment Report", S["subtitle"]),
        Paragraph("PMFBY Claim Evidence Document", S["subtitle"]),
    ]]
    header_table = Table([[
        Paragraph("<b>AGROTILTIX</b><br/>AI Crop Damage Assessment Report", S["title"]),
    ]], colWidths=[174*mm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), GREEN_DARK),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("ROUNDEDCORNERS", [6]),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 3*mm))

    # Subtitle row
    subtitle_data = [[
        Paragraph("Pradhan Mantri Fasal Bima Yojana (PMFBY) — Digital Claim Evidence", S["subtitle"])
    ]]
    sub_table = Table(subtitle_data, colWidths=[174*mm])
    sub_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), GREEN_MID),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(sub_table)
    story.append(Spacer(1, 5*mm))

    # ── REPORT META ──────────────────────────────────────────────────────────
    report_date = datetime.now().strftime("%d %B %Y")
    report_time = datetime.now().strftime("%I:%M %p")
    report_id   = datetime.now().strftime("AGT-%Y%m%d-%H%M%S")

    meta_data = [
        ["Report ID:", report_id, "Date:", report_date],
        ["Assessment Time:", report_time, "System:", "FarmRakshak AI v2.0"],
    ]
    meta_table = Table(meta_data, colWidths=[35*mm, 52*mm, 30*mm, 57*mm])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), GREY_LIGHT),
        ("TEXTCOLOR",     (0, 0), (0, -1), GREY_MID),
        ("TEXTCOLOR",     (2, 0), (2, -1), GREY_MID),
        ("FONTNAME",      (0, 0), (-1, -1), "Helvetica"),
        ("FONTNAME",      (1, 0), (1, -1), "Helvetica-Bold"),
        ("FONTNAME",      (3, 0), (3, -1), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 8.5),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("GRID",          (0, 0), (-1, -1), 0.3, colors.HexColor("#E5E7EB")),
        ("ROUNDEDCORNERS", [4]),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 5*mm))

    # ── FARMER DETAILS SECTION ────────────────────────────────────────────────
    def section_header(text):
        t = Table([[Paragraph(f"  {text}", S["section_head"])]], colWidths=[174*mm])
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), GREEN_MID),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("ROUNDEDCORNERS", [4]),
        ]))
        return t

    story.append(section_header("SECTION 1 — FARMER & FIELD DETAILS"))
    story.append(Spacer(1, 2*mm))

    farmer_data = [
        ["Farmer Name",     farmer_name or "—",     "Village",       village or "—"],
        ["District",        district or "—",         "State",         state or "—"],
        ["Crop",            crop or "—",             "Area (Acres)",  str(acres)],
        ["Survey/Khasra",   survey_number or "N/A",  "Policy Number", policy_number or "N/A"],
        ["Bank Branch",     bank_branch or "N/A",    "Season",        "Kharif / Rabi 2024-25"],
    ]
    farmer_table = Table(farmer_data, colWidths=[35*mm, 52*mm, 32*mm, 55*mm])
    farmer_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (0, -1), GREEN_BG),
        ("BACKGROUND",    (2, 0), (2, -1), GREEN_BG),
        ("TEXTCOLOR",     (0, 0), (0, -1), GREEN_DARK),
        ("TEXTCOLOR",     (2, 0), (2, -1), GREEN_DARK),
        ("FONTNAME",      (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME",      (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTNAME",      (1, 0), (1, -1), "Helvetica"),
        ("FONTNAME",      (3, 0), (3, -1), "Helvetica"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#D1FAE5")),
    ]))
    story.append(farmer_table)
    story.append(Spacer(1, 5*mm))

    # ── AI ASSESSMENT SECTION ─────────────────────────────────────────────────
    story.append(section_header("SECTION 2 — AI DAMAGE ASSESSMENT"))
    story.append(Spacer(1, 3*mm))

    # Big verdict
    verdict_labels = {
        "healthy":  "NO LODGING DETECTED",
        "mild":     "MILD LODGING DETECTED",
        "moderate": "MODERATE LODGING DETECTED",
        "severe":   "SEVERE LODGING DETECTED",
    }
    verdict_text = verdict_labels.get(pred, pred.upper())

    verdict_table = Table([[Paragraph(verdict_text, S["verdict"])]], colWidths=[174*mm])
    verdict_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), sev_color),
        ("TEXTCOLOR",     (0, 0), (-1, -1), WHITE),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("ROUNDEDCORNERS", [6]),
    ]))
    story.append(verdict_table)
    story.append(Spacer(1, 3*mm))

    # Assessment metrics table
    class_probs = result.get("class_probs", {})
    prob_str = "  |  ".join([f"{k.title()}: {v}%" for k, v in class_probs.items()])

    assessment_data = [
        ["Parameter", "Value", "Interpretation"],
        ["Predicted Status",  pred.title(),         verdict_labels.get(pred, "")],
        ["Lodging Severity",  f"{sev:.1f}%",        _severity_interpretation(pred)],
        ["AI Confidence",     f"{conf:.1f}%",        _confidence_interpretation(conf)],
        ["Class Probabilities", prob_str,            "Softmax output from EfficientNet-B0"],
        ["Assessment Method", "Deep Learning CNN",  "EfficientNet-B0 Transfer Learning"],
    ]
    assess_table = Table(assessment_data, colWidths=[42*mm, 50*mm, 82*mm])
    assess_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  GREEN_DARK),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  WHITE),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTNAME",      (0, 1), (0, -1),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 8.5),
        ("BACKGROUND",    (0, 1), (-1, 1),  colors.HexColor(f"{sev_color.hexval()}") if hasattr(sev_color, 'hexval') else GREY_LIGHT),
        ("BACKGROUND",    (0, 2), (-1, 2),  GREY_LIGHT),
        ("BACKGROUND",    (0, 3), (-1, 3),  colors.HexColor("#FAFAFA")),
        ("BACKGROUND",    (0, 4), (-1, 4),  GREY_LIGHT),
        ("BACKGROUND",    (0, 5), (-1, 5),  colors.HexColor("#FAFAFA")),
        ("TEXTCOLOR",     (0, 1), (0, -1),  GREEN_DARK),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 7),
        ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#E5E7EB")),
    ]))
    story.append(assess_table)
    story.append(Spacer(1, 5*mm))

    # ── FINANCIAL IMPACT SECTION ──────────────────────────────────────────────
    if yield_data:
        story.append(section_header("SECTION 3 — ESTIMATED FINANCIAL IMPACT"))
        story.append(Spacer(1, 3*mm))

        fin_data = [
            ["Financial Parameter", "Amount (INR)"],
            ["Total Crop Value (at MSP)",        f"Rs. {yield_data.get('gross_value_inr', 0):,.0f}"],
            ["MSP Rate per Quintal",              f"Rs. {yield_data.get('msp_per_qtl', 0):,.0f}"],
            ["Expected Yield",                    f"{yield_data.get('expected_yield_qtl', 0):.1f} quintals / {acres} acres"],
            ["Estimated Loss (Lower Bound)",      f"Rs. {yield_data.get('loss_low_inr', 0):,.0f}  ({yield_data.get('loss_pct_low', 0):.0f}%)"],
            ["Estimated Loss (Upper Bound)",      f"Rs. {yield_data.get('loss_high_inr', 0):,.0f}  ({yield_data.get('loss_pct_high', 0):.0f}%)"],
            ["Claim-Eligible Range",              f"Rs. {yield_data.get('loss_low_inr', 0):,.0f} — Rs. {yield_data.get('loss_high_inr', 0):,.0f}"],
        ]
        fin_table = Table(fin_data, colWidths=[90*mm, 84*mm])
        fin_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0),  GREEN_DARK),
            ("TEXTCOLOR",     (0, 0), (-1, 0),  WHITE),
            ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTNAME",      (0, 1), (0, -1),  "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, -1), 9),
            ("BACKGROUND",    (0, -1), (-1, -1), GREEN_BG),
            ("TEXTCOLOR",     (0, -1), (-1, -1), GREEN_DARK),
            ("FONTNAME",      (0, -1), (-1, -1), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, GREY_LIGHT]),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 10),
            ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#E5E7EB")),
        ]))
        story.append(fin_table)
        story.append(Spacer(1, 5*mm))

    # ── RECOMMENDATION SECTION ────────────────────────────────────────────────
    rec_texts = {
        "healthy":  "Crop is healthy. No insurance claim action required at this time. Continue regular field monitoring.",
        "mild":     "Mild lodging detected. Monitor field over next 3-5 days. If damage progresses, document with additional photographs and notify your insurance company immediately.",
        "moderate": "Significant lodging detected. Notify your PMFBY insurance provider within 72 hours of damage. Submit this report along with additional field photographs as supporting evidence for your insurance claim. Contact your local Krishi Vigyan Kendra (KVK) for immediate agronomical support.",
        "severe":   "URGENT: Severe crop lodging detected. Immediately notify your PMFBY insurance company and local agriculture officer. This report serves as primary digital evidence of crop damage. Do NOT harvest until the insurance surveyor has conducted their assessment, unless further delay will increase losses. File your claim within the stipulated time period under PMFBY guidelines.",
    }

    sec_num = 4 if yield_data else 3
    story.append(section_header(f"SECTION {sec_num} — RECOMMENDATIONS & NEXT STEPS"))
    story.append(Spacer(1, 3*mm))

    rec_color_map = {
        "healthy": colors.HexColor("#D1FAE5"),
        "mild": colors.HexColor("#FEF9C3"),
        "moderate": colors.HexColor("#FFEDD5"),
        "severe": colors.HexColor("#FEE2E2"),
    }
    rec_bg = rec_color_map.get(pred, GREY_LIGHT)
    rec_table = Table([[Paragraph(rec_texts.get(pred, ""), S["body"])]], colWidths=[174*mm])
    rec_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), rec_bg),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("ROUNDEDCORNERS", [4]),
    ]))
    story.append(rec_table)
    story.append(Spacer(1, 5*mm))

    # ── PMFBY HELPLINE INFO ───────────────────────────────────────────────────
    story.append(section_header(f"SECTION {sec_num+1} — PMFBY CONTACT INFORMATION"))
    story.append(Spacer(1, 2*mm))

    contact_data = [
        ["PMFBY National Helpline", "14447"],
        ["Crop Insurance Portal",   "pmfby.gov.in"],
        ["Farmer Helpline",         "1800-180-1551 (Toll Free)"],
        ["Grievance Portal",        "pgportal.gov.in"],
    ]
    contact_table = Table(contact_data, colWidths=[80*mm, 94*mm])
    contact_table.setStyle(TableStyle([
        ("FONTNAME",      (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("TEXTCOLOR",     (0, 0), (0, -1), GREEN_DARK),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE, GREY_LIGHT]),
        ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#E5E7EB")),
    ]))
    story.append(contact_table)
    story.append(Spacer(1, 6*mm))

    # ── DECLARATION ──────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=GREEN_LIGHT))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "DECLARATION: This report has been generated by FarmRakshak AI system using computer vision analysis "
        "of the submitted crop field photograph. The AI assessment is based on EfficientNet-B0 deep learning "
        "model trained on crop lodging data. This document is intended to serve as supplementary digital evidence "
        "for PMFBY crop insurance claims and should be submitted alongside official claim forms. "
        "Final claim settlement is subject to verification by authorized PMFBY surveyors.",
        S["disclaimer"]
    ))
    story.append(Spacer(1, 3*mm))

    # Signature area
    sig_data = [[
        Paragraph("_______________________\nFarmer Signature", S["disclaimer"]),
        Paragraph("_______________________\nAgricultural Officer", S["disclaimer"]),
        Paragraph("_______________________\nInsurance Company Rep.", S["disclaimer"]),
    ]]
    sig_table = Table(sig_data, colWidths=[58*mm, 58*mm, 58*mm])
    sig_table.setStyle(TableStyle([
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(sig_table)
    story.append(Spacer(1, 3*mm))

    story.append(Paragraph(
        f"Report generated on {report_date} at {report_time} | Report ID: {report_id} | "
        "FarmRakshak — AI for Indian Farmers | pmfby.gov.in",
        S["footer"]
    ))

    doc.build(story)
    buf.seek(0)
    return buf


def _severity_interpretation(pred: str) -> str:
    interp = {
        "healthy":  "No structural damage — crop standing upright",
        "mild":     "Minor tilting observed — early intervention recommended",
        "moderate": "Significant damage — yield loss likely without action",
        "severe":   "Critical damage — urgent harvesting/support needed",
    }
    return interp.get(pred, "")


def _confidence_interpretation(confidence: float) -> str:
    if confidence >= 85:
        return "Very High — Assessment highly reliable"
    elif confidence >= 70:
        return "High — Assessment reliable"
    elif confidence >= 55:
        return "Moderate — Consider field verification"
    else:
        return "Low — Manual verification strongly recommended"
