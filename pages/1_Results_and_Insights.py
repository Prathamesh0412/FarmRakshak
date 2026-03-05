import streamlit as st
from PIL import Image
from app import inject_css, ensure_i18n, render_results

st.set_page_config(page_title="Results • FarmRakshak", page_icon="📊", layout="wide")
inject_css()
lang_code, tr = ensure_i18n()

st.markdown(f"""
<div class="hero">
    <h1>Results & Insights</h1>
    <p>{tr.get('results_title','Assessment Results')}</p>
    <div class="hero-tags">
        <span class="hero-tag">📊 Insights</span>
        <span class="hero-tag">🔊 Voice</span>
        <span class="hero-tag">🌾 Lodging</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

if "last_result" not in st.session_state or "last_image" not in st.session_state:
    st.info("Upload an image on Home to view results.")
    st.page_link("app.py", label="Go to Home →")
else:
    render_results(
        st.session_state["last_result"],
        st.session_state.get("last_image", Image.new("RGB", (224, 224))),
        st.session_state["translations"],
        st.session_state.get("lang_code", "en")
    )

st.markdown("---")
nav = st.columns(4)
nav[0].page_link("app.py", label="Home / Upload")
nav[1].page_link("pages/2_Yield_Loss_Estimator.py", label=tr.get("yield_tab","Yield Loss (₹)"))
nav[2].page_link("pages/3_Field_History.py", label=tr.get("history_tab","Field History"))
nav[3].page_link("pages/4_PMF_BY_Report.py", label=tr.get("pmfby_tab","PMFBY Report"))
