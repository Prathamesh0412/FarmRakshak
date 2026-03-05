import streamlit as st
from app import inject_css, ensure_i18n, render_pmfby

st.set_page_config(page_title="PMFBY Report • FarmRakshak", page_icon="🏛️", layout="wide")
inject_css()
lang_code, tr = ensure_i18n()

st.markdown(f"""
<div class="hero">
    <h1>PMFBY Report</h1>
    <p>{tr.get('pmfby_title','PMFBY Insurance Claim Report')}</p>
    <div class="hero-tags">
        <span class="hero-tag">🏛️ PMFBY</span>
        <span class="hero-tag">📄 PDF</span>
        <span class="hero-tag">🌾 Claims</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

if "last_result" not in st.session_state:
    st.info("Run an analysis on Home to generate a report.")
    st.page_link("app.py", label="Go to Home →")
else:
    render_pmfby(st.session_state["last_result"], tr)

st.markdown("---")
nav = st.columns(4)
nav[0].page_link("app.py", label="Home / Upload")
nav[1].page_link("pages/1_Results_and_Insights.py", label=tr.get("results_title","Results"))
nav[2].page_link("pages/2_Yield_Loss_Estimator.py", label=tr.get("yield_tab","Yield Loss (₹)"))
nav[3].page_link("pages/3_Field_History.py", label=tr.get("history_tab","Field History"))
