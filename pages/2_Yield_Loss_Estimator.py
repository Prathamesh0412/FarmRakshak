import streamlit as st
from app import inject_css, ensure_i18n, render_yield_estimator

st.set_page_config(page_title="Yield Loss • FarmRakshak", page_icon="💸", layout="wide")
inject_css()
lang_code, tr = ensure_i18n()

st.markdown(f"""
<div class="hero">
    <h1>Yield Loss Estimator</h1>
    <p>{tr.get('yield_estimator_title','Yield Loss Estimator (₹)')}</p>
    <div class="hero-tags">
        <span class="hero-tag">💰 Loss</span>
        <span class="hero-tag">🌱 Crop</span>
        <span class="hero-tag">📊 Insights</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

if "last_result" not in st.session_state:
    st.info("Run an analysis on Home first to estimate loss.")
    st.page_link("app.py", label="Go to Home →")
else:
    render_yield_estimator(st.session_state["last_result"], tr)

st.markdown("---")
nav = st.columns(4)
nav[0].page_link("app.py", label="Home / Upload")
nav[1].page_link("pages/1_Results_and_Insights.py", label=tr.get("results_title","Results"))
nav[2].page_link("pages/3_Field_History.py", label=tr.get("history_tab","Field History"))
nav[3].page_link("pages/4_PMF_BY_Report.py", label=tr.get("pmfby_tab","PMFBY Report"))
