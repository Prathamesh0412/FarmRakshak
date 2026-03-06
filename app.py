# =====================================================================
# app.py - FarmRakshak v2.0 - Upgraded Full-Stack AI Application
# Features: TTS | Yield Estimator | Field History | PMFBY Reports
# =====================================================================

import os, json, base64
import streamlit as st
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from datetime import datetime

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
TRANSLATIONS_DIR = os.path.join(BASE_DIR, "translations")

# ── Language Config ────────────────────────────────────────────────────────────
LANGUAGES = {"English": "en", "हिंदी": "hi", "मराठी": "mr"}

CLASS_COLORS = {"healthy":"#27AE60","mild":"#F59E0B","moderate":"#E67E22","severe":"#E74C3C"}
SEVERITY_EMOJI = {"healthy":"✅","mild":"⚠️","moderate":"🔶","severe":"🚨"}
TREND_ICONS = {"worsening":"📈🔴","improving":"📉🟢","stable":"➡️🟡","insufficient_data":"ℹ️"}

# ── Translation Loader ─────────────────────────────────────────────────────────
@st.cache_data
def load_translations(lang_code):
    path = os.path.join(TRANSLATIONS_DIR, f"{lang_code}.json")
    if not os.path.exists(path):
        path = os.path.join(TRANSLATIONS_DIR, "en.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def t(key):
    return st.session_state.get("translations", {}).get(key, key)


def ensure_i18n(default_lang="English"):
    """Ensure translations and lang_code are in session; return (lang_code, tr)."""
    lang_code = st.session_state.get("lang_code")
    if not lang_code:
        lang_code = LANGUAGES.get(default_lang, "en")
    tr = st.session_state.get("translations") or load_translations(lang_code)
    st.session_state["translations"] = tr
    st.session_state["lang_code"] = lang_code
    return lang_code, tr

# ── CSS Injection ──────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@300;400;500;600&display=swap');
    html,body,[class*="css"]{font-family:'DM Sans',sans-serif;background:#F4F7F0;}
    #MainMenu,footer{visibility:hidden;}
    .block-container{padding-top:1.2rem;max-width:1120px;}
    .hero{background:linear-gradient(140deg,#0A3D0C,#1B5E20 50%,#2E7D32);padding:2.2rem 2.5rem 1.8rem;border-radius:18px;margin-bottom:1.5rem;position:relative;overflow:hidden;}
    .hero::after{content:"\U0001f33e";position:absolute;right:1.5rem;top:50%;transform:translateY(-50%);font-size:6rem;opacity:0.1;}
    .hero h1{font-family:'Playfair Display',serif;font-size:2.5rem;color:#fff;margin:0;}
    .hero h1 em{color:#81C784;font-style:normal;}
    .hero p{color:#C8E6C9;font-size:0.92rem;margin:0.4rem 0 0;max-width:580px;}
    .hero-tags{display:flex;gap:0.5rem;flex-wrap:wrap;margin-top:0.8rem;}
    .hero-tag{display:inline-block;background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.25);color:#fff;font-size:0.68rem;font-weight:600;padding:0.18rem 0.55rem;border-radius:999px;text-transform:uppercase;letter-spacing:0.5px;}
    .card{background:#fff;border-radius:14px;border:1px solid #DDE8D5;padding:1.3rem 1.4rem;box-shadow:0 2px 10px rgba(0,0,0,0.04);margin-bottom:1rem;}
    .card-title{font-family:'Playfair Display',serif;font-size:1rem;color:#1B5E20;margin-bottom:0.8rem;display:flex;align-items:center;gap:0.4rem;}
    .result-pill{display:inline-flex;align-items:center;gap:0.4rem;font-size:1rem;font-weight:600;padding:0.4rem 1rem;border-radius:999px;margin-bottom:0.6rem;}
    .sev-bar{background:#E8F0E2;border-radius:999px;height:13px;overflow:hidden;margin:0.3rem 0;}
    .sev-fill{height:100%;border-radius:999px;transition:width 0.8s;}
    .metric{background:#F4F7F0;border:1px solid #DDE8D5;border-radius:10px;padding:0.75rem;text-align:center;}
    .metric-lbl{font-size:0.67rem;color:#7A8A70;text-transform:uppercase;letter-spacing:0.8px;font-weight:600;}
    .metric-val{font-family:'Playfair Display',serif;font-size:1.6rem;line-height:1.2;}
    .rec-box{padding:0.85rem 1.1rem;border-radius:10px;border-left:4px solid;font-size:0.88rem;line-height:1.7;}
    .rupee-highlight{background:linear-gradient(135deg,#FFF9C4,#FFF3CD);border:1.5px solid #F59E0B;border-radius:12px;padding:1rem 1.2rem;margin:0.5rem 0;}
    .rupee-main{font-family:'Playfair Display',serif;font-size:1.9rem;color:#92400E;font-weight:700;}
    .history-card{background:#F9FBF6;border:1px solid #DDE8D5;border-radius:10px;padding:0.7rem;margin-bottom:0.5rem;}
    .trend-worsening{color:#DC2626;font-weight:700;}
    .trend-improving{color:#10B981;font-weight:700;}
    .trend-stable{color:#F59E0B;font-weight:700;}
    .stButton>button{background:linear-gradient(135deg,#2D6A2F,#1B4D1F)!important;color:white!important;border:none!important;border-radius:10px!important;font-weight:600!important;width:100%!important;min-height:2.6rem!important;}
    .stButton>button:hover{opacity:0.88!important;}
    .stTabs [data-baseweb="tab-list"]{gap:0.5rem;background:#E8F0E2;padding:0.3rem;border-radius:10px;}
    .stTabs [data-baseweb="tab"]{border-radius:8px;padding:0.4rem 1rem;font-weight:500;}
    .stTabs [aria-selected="true"]{background:#1B5E20!important;color:white!important;}
    .footer{text-align:center;color:#9BA88F;font-size:0.75rem;padding:1.2rem 0 0.4rem;border-top:1px solid #DDE8D5;margin-top:1.5rem;}
    [data-testid="stFileUploader"] label{display:none!important;}
    </style>
    """, unsafe_allow_html=True)

# ── Demo Predict ───────────────────────────────────────────────────────────────
def run_prediction(pil_image):
    from model.inference import predict
    return predict(pil_image, generate_gradcam=False)

# ── Prob Chart ─────────────────────────────────────────────────────────────────
def prob_chart(class_probs, tr):
    classes = list(class_probs.keys())
    values  = list(class_probs.values())
    labels  = [tr.get(c, c.title()) for c in classes]
    colors  = [CLASS_COLORS[c] for c in classes]
    fig, ax = plt.subplots(figsize=(5, 2.4))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#F4F7F0")
    bars = ax.barh(labels[::-1], values[::-1], color=colors[::-1], height=0.52, edgecolor="none")
    for bar, val in zip(bars, values[::-1]):
        ax.text(bar.get_width()+0.5, bar.get_y()+bar.get_height()/2,
                f"{val:.1f}%", va="center", ha="left", fontsize=9, color="#374151")
    ax.set_xlim(0, 120)
    ax.tick_params(labelsize=9, colors="#374151")
    for sp in ["top","right","left"]: ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color("#D1D5DB")
    ax.grid(axis="x", linestyle="--", alpha=0.35, color="#E5E7EB")
    plt.tight_layout(pad=0.4)
    return fig

# ── TTS Section ────────────────────────────────────────────────────────────────
def render_tts(result, tr, lang_code):
    """Renders the Voice Output button using browser Web Speech API."""
    import streamlit.components.v1 as components
    pred = result["predicted_class"]
    sev  = result["severity_pct"]
    conf = result["confidence"]
    pred_label = tr.get(pred, pred)
    rec_text   = tr.get(f"rec_{pred}", "")

    # Build spoken text per language
    voice_map = {"en":"en-IN","hi":"hi-IN","mr":"mr-IN"}
    voice_locale = voice_map.get(lang_code, "en-IN")

    if lang_code == "en":
        speech = f"Crop analysis complete. Status: {pred_label}. Severity: {sev:.0f} percent. Confidence: {conf:.0f} percent. Recommendation: {rec_text}"
    elif lang_code == "hi":
        speech = f"\u092b\u0938\u0932 \u0935\u093f\u0936\u094d\u0932\u0947\u0937\u0923 \u092a\u0942\u0930\u093e \u0939\u0941\u0906\u0964 \u0938\u094d\u0925\u093f\u0924\u093f \u0939\u0948: {pred_label}\u0964 \u0917\u0902\u092d\u0940\u0930\u0924\u093e {sev:.0f} \u092a\u094d\u0930\u0924\u093f\u0936\u0924 \u0939\u0948\u0964 {rec_text}"
    else:
        speech = f"\u092a\u093f\u0915 \u0935\u093f\u0936\u094d\u0932\u0947\u0937\u0923 \u092a\u0942\u0930\u094d\u0923 \u091d\u093e\u0932\u0947\u0964 \u0938\u094d\u0925\u093f\u0924\u0940: {pred_label}\u0964 \u0924\u0940\u0935\u094d\u0930\u0924\u093e {sev:.0f} \u091f\u0915\u094d\u0915\u0947\u0964 {rec_text}"

    # Escape for JS
    safe_speech = speech.replace("'", " ").replace('"', " ").replace("`", " ").replace("\\", "")

    tts_html = f"""
    <div style="margin:0.5rem 0 0.3rem;">
      <button onclick="speakNow()" id="tts-btn" style="
          background:linear-gradient(135deg,#1B5E20,#2E7D32);color:white;border:none;
          border-radius:10px;padding:0.5rem 1.2rem;font-size:0.9rem;font-weight:600;
          cursor:pointer;display:inline-flex;align-items:center;gap:0.4rem;
          box-shadow:0 2px 8px rgba(27,94,32,0.25);">
        &#128266; {tr.get("speak_result","Speak Result")}
      </button>
      <button onclick="stopNow()" style="
          background:#6B7280;color:white;border:none;border-radius:10px;
          padding:0.5rem 0.9rem;font-size:0.9rem;font-weight:600;cursor:pointer;
          display:inline-flex;align-items:center;gap:0.3rem;margin-left:0.4rem;">
        &#9646;&#9646; {tr.get("stop_speaking","Stop")}
      </button>
      <div id="tts-status" style="font-size:0.72rem;color:#6B7280;margin-top:0.25rem;min-height:1rem;"></div>
    </div>
    <script>
    function speakNow(){{
        if(!window.speechSynthesis){{
            document.getElementById("tts-status").innerText="\u26a0 Not supported in this browser";return;
        }}
        window.speechSynthesis.cancel();
        var u=new SpeechSynthesisUtterance('{safe_speech}');
        u.lang="{voice_locale}";u.rate=0.87;u.pitch=1.0;u.volume=1.0;
        var voices=window.speechSynthesis.getVoices();
        var v=voices.find(x=>x.lang==="{voice_locale}")||voices.find(x=>x.lang.startsWith("{lang_code}"));
        if(v)u.voice=v;
        u.onstart=function(){{document.getElementById("tts-status").innerText="\U0001f4ac Speaking..."}};
        u.onend=function(){{document.getElementById("tts-status").innerText="\u2714 Done";setTimeout(function(){{document.getElementById("tts-status").innerText=""}},2000)}};
        u.onerror=function(e){{document.getElementById("tts-status").innerText="\u26a0 Error: "+e.error}};
        window.speechSynthesis.speak(u);
    }}
    function stopNow(){{window.speechSynthesis.cancel();document.getElementById("tts-status").innerText="";}}
    if(window.speechSynthesis.onvoiceschanged!==undefined){{window.speechSynthesis.onvoiceschanged=function(){{window.speechSynthesis.getVoices();}};}}
    </script>
    """
    components.html(tts_html, height=85)

# ── Yield Estimator Tab ────────────────────────────────────────────────────────
def render_yield_estimator(result, tr):
    """Renders the rupee yield loss estimator panel."""
    from utils.yield_estimator import estimate_loss, CROP_DISPLAY, format_inr

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-title">\U0001f4b0 {tr.get("yield_estimator_title","Yield Loss Estimator (\u20b9)")}</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        crop_options = list(CROP_DISPLAY.keys())
        crop_labels  = [CROP_DISPLAY[c] for c in crop_options]
        selected_idx = st.selectbox(
            tr.get("select_crop","Select Your Crop"),
            options=range(len(crop_options)),
            format_func=lambda i: crop_labels[i],
            key="crop_selector"
        )
        selected_crop = crop_options[selected_idx]
    with col2:
        acres = st.number_input(
            tr.get("field_acres","Field Area (Acres)"),
            min_value=0.1, max_value=100.0, value=1.0, step=0.5,
            key="acres_input"
        )

    pred = result["predicted_class"]
    yd   = estimate_loss(selected_crop, pred, acres)

    # Store for later (PMFBY report use)
    st.session_state["yield_data"]  = yd
    st.session_state["selected_crop"] = selected_crop

    if pred == "healthy":
        st.success(f"\u2705 {tr.get('no_loss_expected','No yield loss expected. Crop is healthy.')}")
    else:
        # Big rupee display
        low_inr  = yd["loss_low_inr"]
        high_inr = yd["loss_high_inr"]
        st.markdown(
            f'<div class="rupee-highlight">'
            f'<div class="metric-lbl" style="color:#92400E;">{tr.get("estimated_loss","Estimated Financial Loss")}</div>'
            f'<div class="rupee-main">{format_inr(low_inr)} \u2014 {format_inr(high_inr)}</div>'
            f'<small style="color:#78350F;">{yd["loss_pct_low"]:.0f}\u2013{yd["loss_pct_high"]:.0f}% of expected yield lost</small>'
            f'</div>',
            unsafe_allow_html=True
        )

    # Breakdown table
    rows = [
        [tr.get("crop","Crop"),             yd["crop"]],
        [tr.get("field_area","Field Area"),  f"{acres} acres"],
        ["MSP Rate",                         f"\u20b9{yd['msp_per_qtl']:,} / quintal"],
        ["Expected Yield",                   f"{yd['expected_yield_qtl']:.1f} quintals"],
        [tr.get("gross_value","Gross Value"), f"\u20b9{yd['gross_value_inr']:,.0f}"],
        [tr.get("loss_range","Loss Range"),  f"\u20b9{yd['loss_low_inr']:,.0f} \u2013 \u20b9{yd['loss_high_inr']:,.0f}"],
    ]

    for row in rows:
        c1, c2 = st.columns([1.2, 2])
        c1.markdown(f"**{row[0]}**")
        c2.write(row[1])

    st.caption(f"\U0001f4cb MSP source: CACP Kharif 2024-25 | ICAR average yield data")
    st.markdown("</div>", unsafe_allow_html=True)
    return yd

# ── Field History Tab ─────────────────────────────────────────────────────────
def render_field_history(current_result, current_image, tr):
    """Renders before/after field comparison panel."""
    from utils.field_history import (
        save_snapshot, get_history, load_snapshot_image,
        get_trend, image_to_base64
    )

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-title">\U0001f4f8 {tr.get("field_history_title","Field History & Trend Tracker")}</div>', unsafe_allow_html=True)

    crop_name = st.session_state.get("selected_crop", "wheat")
    acres     = st.session_state.get("acres_input", 1.0)
    farmer    = st.session_state.get("farmer_name", "")
    field_n   = st.session_state.get("field_name", "")

    col_save, col_clear = st.columns([3,1])
    with col_save:
        if st.button(f"\U0001f4be {tr.get('save_snapshot','Save This Snapshot to History')}", key="save_snap"):
            snap_id = save_snapshot(current_image, current_result, crop_name, acres, farmer, field_n)
            st.success(f"\u2714 {tr.get('snapshot_saved','Snapshot saved!')} (ID: {snap_id})")
    with col_clear:
        if st.button(f"\U0001f5d1 {tr.get('clear_history','Clear')}", key="clear_hist"):
            from utils.field_history import clear_history
            clear_history()
            st.info("History cleared.")

    st.markdown("---")
    history = get_history(limit=8)

    if not history:
        st.info(f"\U0001f4f7 {tr.get('no_history','No history yet. Save a snapshot to start tracking field trends.')}")
    else:
        # Trend analysis
        trend = get_trend(history)
        trend_icon = TREND_ICONS.get(trend, "")
        trend_text_map = {
            "worsening":        f"\U0001f534 {tr.get('trend_worsening','Lodging is getting WORSE. Take action immediately.')}",
            "improving":        f"\U0001f7e2 {tr.get('trend_improving','Condition is improving. Continue current management.')}",
            "stable":           f"\U0001f7e1 {tr.get('trend_stable','Condition is STABLE. Monitor regularly.')}",
            "insufficient_data": f"\u2139\ufe0f {tr.get('trend_insufficient','Need more snapshots for trend analysis.')}",
        }
        st.markdown(f"**\U0001f4ca Trend:** {trend_text_map.get(trend,'')}")
        st.markdown("")

        # Show history cards
        for i, record in enumerate(history[:6]):
            sev_pct   = record.get("severity_pct", 0)
            pred_cls  = record.get("predicted_class", "healthy")
            color     = CLASS_COLORS.get(pred_cls, "#6B7280")
            snap_img  = load_snapshot_image(record["id"])

            with st.container():
                c1, c2, c3 = st.columns([1, 2, 2])
                with c1:
                    if snap_img:
                        st.image(snap_img, width=100)
                    else:
                        st.markdown(f'<div style="width:100px;height:80px;background:#E8F0E2;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:1.5rem;">\U0001f33e</div>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f"**{record.get('date_display','—')}**")
                    st.markdown(
                        f'<span style="background:{color}22;color:{color};border:1px solid {color};'
                        f'border-radius:999px;padding:0.15rem 0.6rem;font-size:0.8rem;font-weight:600;">'
                        f'{pred_cls.title()}</span>',
                        unsafe_allow_html=True
                    )
                with c3:
                    st.markdown(f"Severity: **{sev_pct:.1f}%**")
                    st.markdown(f"Crop: {record.get('crop','—')}")

                # Tiny severity mini-bar
                st.markdown(
                    f'<div class="sev-bar" style="height:6px;margin:0.2rem 0 0.6rem;">'
                    f'<div class="sev-fill" style="width:{min(sev_pct,100):.0f}%;background:{color};"></div></div>',
                    unsafe_allow_html=True
                )

    st.markdown("</div>", unsafe_allow_html=True)

# ── PMFBY Report Tab ──────────────────────────────────────────────────────────
def render_pmfby(result, tr):
    """Renders the PMFBY insurance claim report generator."""
    from utils.yield_estimator import CROP_DISPLAY

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-title">\U0001f3db\ufe0f {tr.get("pmfby_title","PMFBY Insurance Claim Report")}</div>', unsafe_allow_html=True)
    st.markdown(f'<p style="font-size:0.85rem;color:#6B7280;margin-top:-0.3rem;">{tr.get("pmfby_subtitle","Generate a digital damage report to submit for your crop insurance claim.")}</p>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        farmer_name = st.text_input(tr.get("farmer_name_label","Farmer Name"), key="farmer_name",
                                    placeholder="e.g. Ramesh Patil")
        village = st.text_input(tr.get("village_label","Village / Taluka"), key="village",
                                placeholder="e.g. Nashik, Kopargaon")
        district = st.text_input(tr.get("district_label","District"), key="district",
                                 placeholder="e.g. Nashik")
    with c2:
        state = st.text_input(tr.get("state_label","State"), value="Maharashtra", key="state")
        policy_no = st.text_input(tr.get("policy_label","PMFBY Policy Number"), key="policy_no",
                                  placeholder="e.g. MH-PMFBY-2024-XXXXX")
        survey_no = st.text_input(tr.get("survey_label","Survey / Khasra Number"), key="survey_no",
                                  placeholder="e.g. 123/A")

    crop_display = CROP_DISPLAY.get(
        st.session_state.get("selected_crop","wheat"),
        "Wheat"
    )
    acres  = st.session_state.get("acres_input", 1.0)
    yd     = st.session_state.get("yield_data", None)

    st.markdown("")
    if st.button(f"\U0001f4e5 {tr.get('generate_report','Generate PMFBY Report (PDF)')}", key="gen_report"):
        if not farmer_name:
            st.warning(f"\u26a0\ufe0f {tr.get('farmer_name_required','Please enter farmer name to generate report.')}")
        else:
            with st.spinner(tr.get("generating_report","Generating PDF report...")):
                try:
                    from utils.pmfby_report import generate_pmfby_report
                    pdf_buf = generate_pmfby_report(
                        farmer_name  = farmer_name,
                        village      = village,
                        district     = district,
                        state        = state,
                        crop         = crop_display,
                        acres        = acres,
                        result       = result,
                        yield_data   = yd,
                        policy_number= policy_no,
                        survey_number= survey_no,
                    )
                    report_date = datetime.now().strftime("%d%m%Y_%H%M")
                    filename = f"PMFBY_Claim_{farmer_name.replace(' ','_')}_{report_date}.pdf"
                    st.download_button(
                        label       = f"\U0001f4c4 {tr.get('download_report','Download PDF Report')}",
                        data        = pdf_buf,
                        file_name   = filename,
                        mime        = "application/pdf",
                    )
                    st.success(f"\u2714 {tr.get('report_ready','Report generated! Click above to download.')}")
                except Exception as e:
                    st.error(f"Report generation failed: {e}")

    # Info boxes
    st.markdown("")
    with st.expander(f"\u2139\ufe0f {tr.get('pmfby_info_title','What is PMFBY?')}"):
        st.markdown(tr.get("pmfby_info_text",
            """**Pradhan Mantri Fasal Bima Yojana (PMFBY)** is India's flagship crop insurance scheme
            implemented across 250,000 panchayats. This digital report replaces the need for an
            insurance agent to physically visit your field.

            **How to use this report:**
            1. Download the PDF report
            2. Call the PMFBY helpline: **14447**
            3. Submit report + field photos to your bank/insurance company
            4. Track claim at **pmfby.gov.in**

            **Important:** File your claim within 72 hours of damage occurrence."""
        ))

    st.markdown("</div>", unsafe_allow_html=True)

# ── Main Result Renderer ───────────────────────────────────────────────────────
def render_results(result, pil_image, tr, lang_code):
    """Main results panel with all features integrated."""
    pred  = result["predicted_class"]
    conf  = result["confidence"]
    sev   = result["severity_pct"]
    probs = result["class_probs"]
    color = CLASS_COLORS[pred]
    emoji = SEVERITY_EMOJI.get(pred, "")
    pred_label = tr.get(pred, pred.title())
    desc_text  = tr.get(f"{pred}_desc", "")
    rec_text   = tr.get(f"rec_{pred}", "")

    # ── Status Card ─────────────────────────────────────────────────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-title">\U0001f4ca {tr.get("results_title","Assessment Results")}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="result-pill" style="background:{color}22;color:{color};border:1.5px solid {color};">'
        f'{emoji} {pred_label}</div><br>'
        f'<span style="font-size:0.84rem;color:#6B7280;">{desc_text}</span>',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="metric"><div class="metric-lbl">{tr.get("severity_label","Severity")}</div><div class="metric-val" style="color:{color}">{sev:.1f}%</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric"><div class="metric-lbl">{tr.get("confidence_label","Confidence")}</div><div class="metric-val">{conf:.1f}%</div></div>', unsafe_allow_html=True)
    with c3:
        badge = tr.get(f"badge_{pred}", pred.upper())
        st.markdown(f'<div class="metric"><div class="metric-lbl">Status</div><div class="metric-val" style="font-size:0.95rem;color:{color}">{badge}</div></div>', unsafe_allow_html=True)

    st.markdown(f'<br><b>{tr.get("severity_label","Severity")}</b>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="sev-bar"><div class="sev-fill" style="width:{min(sev,100):.1f}%;background:{color};"></div></div>'
        f'<small style="color:#9BA88F">{sev:.1f} {tr.get("severity_unit","% lodging")}</small>',
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Voice Output ─────────────────────────────────────────────────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-title">\U0001f508 {tr.get("voice_output_title","Voice Output")}</div>', unsafe_allow_html=True)
    st.markdown(f'<p style="font-size:0.8rem;color:#6B7280;margin-top:-0.4rem;">{tr.get("voice_output_hint","Hear the result spoken aloud in your language.")}</p>', unsafe_allow_html=True)
    render_tts(result, tr, lang_code)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Probability Chart ─────────────────────────────────────────────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-title">\U0001f4c8 {tr.get("probability_title","Class Probabilities")}</div>', unsafe_allow_html=True)
    fig = prob_chart(probs, tr)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Recommendation ────────────────────────────────────────────────────────────
    rec_styles = {
        "healthy":  ("#D1FAE5","#065F46","#10B981"),
        "mild":     ("#FEF9C3","#78350F","#F59E0B"),
        "moderate": ("#FFEDD5","#7C2D12","#F97316"),
        "severe":   ("#FEE2E2","#7F1D1D","#EF4444"),
    }
    bg, tc, bc = rec_styles.get(pred, ("#F3F4F6","#111827","#6B7280"))
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-title">\U0001f4a1 {tr.get("recommendation_label","Recommendation")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="rec-box" style="background:{bg};color:{tc};border-left-color:{bc};">{rec_text}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Feature Tabs ──────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs([
        f"\U0001f4b0 {tr.get('yield_tab','Yield Loss (\u20b9')}",
        f"\U0001f4f8 {tr.get('history_tab','Field History')}",
        f"\U0001f3db\ufe0f {tr.get('pmfby_tab','PMFBY Report')}",
    ])
    with tab1:
        yd = render_yield_estimator(result, tr)
    with tab2:
        render_field_history(result, pil_image, tr)
    with tab3:
        render_pmfby(result, tr)

# ── MAIN APP ───────────────────────────────────────────────────────────────────
def main():
    st.set_page_config(
        page_title="FarmRakshak v2",
        page_icon="🌾",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    inject_css()

    # Sidebar: language + farmer info
    with st.sidebar:
        st.markdown("### \U0001f310 Language / \u092d\u093e\u0937\u093e")
        lang_choice = st.selectbox("lang", list(LANGUAGES.keys()), label_visibility="collapsed")
        lang_code   = LANGUAGES[lang_choice]
        tr = load_translations(lang_code)
        st.session_state["translations"] = tr
        st.session_state["lang_code"]    = lang_code

        st.markdown("---")
        st.markdown("### \U0001f9d1\u200d\U0001f33e Farmer Info")
        st.text_input("Farmer Name", key="farmer_name_sidebar",
                      placeholder="Your name (for reports)",
                      on_change=lambda: st.session_state.update({"farmer_name": st.session_state.farmer_name_sidebar}))
        st.text_input("Field Name", key="field_name_sidebar",
                      placeholder="e.g. North Plot, Khet 2",
                      on_change=lambda: st.session_state.update({"field_name": st.session_state.field_name_sidebar}))

        st.markdown("---")
        st.markdown("### \U0001f4ca App Info")
        st.caption("FarmRakshak v2.0\nEfficientNet-B0 | PyTorch\n4-Class Lodging Detection")
        st.caption("Features:\n\u2714 Voice Output\n\u2714 Yield Loss \u20b9\n\u2714 Field History\n\u2714 PMFBY Report")

    lang_code, tr = ensure_i18n(lang_choice)

    # ── Hero Section ─────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="hero">
        <h1>Farm<em>Rakshak</em> <span style="font-size:1rem;font-weight:400;color:#A5D6A7;">v2.0</span></h1>
        <p>{tr.get('subtitle','AI-Powered Crop Lodging Detection')}</p>
        <div class="hero-tags">
            <span class="hero-tag">\U0001f508 Voice Output</span>
            <span class="hero-tag">\U0001f4b0 Yield Loss \u20b9</span>
            <span class="hero-tag">\U0001f4f8 Field History</span>
            <span class="hero-tag">\U0001f3db\ufe0f PMFBY Claims</span>
            <span class="hero-tag">\U0001f1ee\U0001f1f3 Hindi | Marathi</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Two-Column Layout ──────────────────────────────────────────────────────
    left, right = st.columns([1, 1.15], gap="large")

    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div class="card-title">\U0001f4f7 {tr.get("upload_label","Upload Field Image")}</div>', unsafe_allow_html=True)
        st.caption(tr.get("upload_hint","JPG, JPEG, PNG supported"))
        uploaded = st.file_uploader("up", type=["jpg","jpeg","png"], label_visibility="collapsed")
        if uploaded:
            img = Image.open(uploaded)
            st.image(img, caption=tr.get("uploaded_image","Uploaded Image"), use_column_width=True)
            st.caption(f"\U0001f4d0 {img.size[0]} \u00d7 {img.size[1]} px")
        st.markdown("</div>", unsafe_allow_html=True)

        btn = st.button(
            f"\U0001f50d {tr.get('predict_button','Analyze Crop Health')}",
            disabled=(uploaded is None)
        )

        with st.expander(f"\u2139\ufe0f {tr.get('about_title','About FarmRakshak')}"):
            st.write(tr.get("about_text",""))
            st.markdown("**Severity:** Healthy(0%) | Mild(15%) | Moderate(35%) | Severe(65%+)")

    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div class="card-title">\U0001f4ca {tr.get("results_title","Assessment Results")}</div>', unsafe_allow_html=True)
        if uploaded is None and "last_result" not in st.session_state:
            st.markdown(
                f'<div style="background:#fff;border:2px dashed #C5D9B8;border-radius:14px;height:320px;'
                f'display:flex;flex-direction:column;align-items:center;justify-content:center;'
                f'text-align:center;color:#9BA88F;padding:2rem;">'
                f'<div style="font-size:3.2rem;margin-bottom:0.6rem;">\U0001f33e</div>'
                f'<div style="font-weight:500;color:#7A8A70;font-size:1rem;">{tr.get("no_image","Upload an image to begin")}</div>'
                f'<div style="font-size:0.82rem;margin-top:0.3rem;">{tr.get("upload_hint","JPG PNG")}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        elif btn:
            with st.spinner(tr.get("analyzing","Analyzing your crop field...")):
                try:
                    img = Image.open(uploaded)
                    result = run_prediction(img)
                    st.session_state["last_result"] = result
                    st.session_state["last_image"]  = img
                except Exception as e:
                    err_text = str(e)
                    if "Trained model not found" in err_text:
                        st.error(
                            "Model is not trained yet. Please run `python model/train.py` "
                            "after adding data to `data/train` and `data/val`."
                        )
                    else:
                        st.error(f"{tr.get('error_title','Error')}: {e}")
                    return
            st.success(tr.get("report_ready","Analysis complete."))
            st.page_link("pages/1_Results_and_Insights.py", label=tr.get("results_title","Assessment Results") + " →")

        elif "last_result" in st.session_state:
            result = st.session_state["last_result"]
            pred  = result.get("predicted_class","—")
            sev   = result.get("severity_pct",0)
            conf  = result.get("confidence",0)
            color = CLASS_COLORS.get(pred, "#1B5E20")
            emoji = SEVERITY_EMOJI.get(pred, "")
            st.markdown(
                f'<div class="result-pill" style="background:{color}22;color:{color};border:1.5px solid {color};">'
                f'{emoji} {tr.get(pred, pred.title())}</div>',
                unsafe_allow_html=True
            )
            st.markdown(f"**{tr.get('severity_label','Severity')}:** {sev:.1f}% | **{tr.get('confidence_label','Confidence')}:** {conf:.1f}%")
            st.page_link("pages/1_Results_and_Insights.py", label=tr.get("results_title","Assessment Results") + " →")
            st.page_link("pages/2_Yield_Loss_Estimator.py", label=tr.get("yield_tab","Yield Loss (₹)") + " →")

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Quick navigation")
    nav_cols = st.columns(4)
    nav_cols[0].page_link("pages/1_Results_and_Insights.py", label="Results")
    nav_cols[1].page_link("pages/2_Yield_Loss_Estimator.py", label="Yield Loss (₹)")
    nav_cols[2].page_link("pages/3_Field_History.py", label="Field History")
    nav_cols[3].page_link("pages/4_PMF_BY_Report.py", label="PMFBY Report")

    st.markdown(f'<div class="footer">{tr.get("footer","FarmRakshak v2.0 2024 - Protecting Farmers with AI")}</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
