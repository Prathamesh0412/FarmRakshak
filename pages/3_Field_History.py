import streamlit as st
from app import inject_css, ensure_i18n, render_field_history

st.set_page_config(page_title="Field History • FarmRakshak", page_icon="📷", layout="wide")
inject_css()
lang_code, tr = ensure_i18n()

st.markdown(f"""
<div class="hero">
    <h1>Field History</h1>
    <p>{tr.get('field_history_title','Field History & Trend Tracker')}</p>
    <div class="hero-tags">
        <span class="hero-tag">📷 Snapshots</span>
        <span class="hero-tag">📈 Trend</span>
        <span class="hero-tag">🌾 Crop</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

if "last_result" not in st.session_state or "last_image" not in st.session_state:
    st.info("Analyze a field first to save and review history.")
    st.page_link("app.py", label="Go to Home →")
else:
    render_field_history(
        st.session_state["last_result"],
        st.session_state["last_image"],
        tr
    )

st.markdown("---")
nav = st.columns(4)
nav[0].page_link("app.py", label="Home / Upload")
nav[1].page_link("pages/1_Results_and_Insights.py", label=tr.get("results_title","Results"))
nav[2].page_link("pages/2_Yield_Loss_Estimator.py", label=tr.get("yield_tab","Yield Loss (₹)"))
nav[3].page_link("pages/4_PMF_BY_Report.py", label=tr.get("pmfby_tab","PMFBY Report"))
