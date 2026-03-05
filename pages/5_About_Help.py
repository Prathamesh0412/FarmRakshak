import streamlit as st
from app import inject_css, ensure_i18n

st.set_page_config(page_title="About • FarmRakshak", page_icon="ℹ️", layout="wide")
inject_css()
lang_code, tr = ensure_i18n()

st.markdown(f"""
<div class="hero">
    <h1>About & Help</h1>
    <p>{tr.get('about_title','About FarmRakshak')}</p>
    <div class="hero-tags">
        <span class="hero-tag">ℹ️ Overview</span>
        <span class="hero-tag">🌾 Farmers</span>
        <span class="hero-tag">🧠 AI</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

st.subheader(tr.get("about_title","About"))
st.write(tr.get("about_text",""))
st.markdown("**Model**: EfficientNet-B0 | PyTorch | 4 classes")
st.markdown("**Features**: Voice output, Yield Loss Estimator, Field History, PMFBY PDF report")

st.markdown("---")
st.subheader("How to use")
st.markdown("1. Go to Home, choose language, and upload a field image.\n2. View results and insights.\n3. Jump to Yield Loss, Field History, or PMFBY pages for deeper actions.")

st.markdown("---")
nav = st.columns(3)
nav[0].page_link("app.py", label="Home / Upload")
nav[1].page_link("pages/1_Results_and_Insights.py", label=tr.get("results_title","Results"))
nav[2].page_link("pages/4_PMF_BY_Report.py", label=tr.get("pmfby_tab","PMFBY Report"))
