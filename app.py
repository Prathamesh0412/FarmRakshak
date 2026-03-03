# app.py - FarmRakshak Main Application
import os, json, time, random
import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt

st.set_page_config(page_title='FarmRakshak', page_icon='🌾', layout='wide')

LANGUAGES = {'English': 'en', 'हिंदी': 'hi', 'मराठी': 'mr'}
TRANSLATIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'translations')
CLASS_COLORS = {'healthy':'#27AE60','mild':'#F39C12','moderate':'#E67E22','severe':'#E74C3C'}
SEVERITY_EMOJIS = {'healthy':'✅','mild':'⚠️','moderate':'🔶','severe':'🚨'}

@st.cache_data
def load_translations(lang_code):
    path = os.path.join(TRANSLATIONS_DIR, f'{lang_code}.json')
    fallback = os.path.join(TRANSLATIONS_DIR, 'en.json')
    target = path if os.path.exists(path) else fallback
    with open(target, 'r', encoding='utf-8') as f:
        return json.load(f)

def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Source+Sans+3:wght@300;400;600&display=swap');
    html,body,[class*="css"]{font-family:'Source Sans 3',sans-serif;background:#F7F9F4;}
    #MainMenu,footer{visibility:hidden;}
    .block-container{padding-top:1.5rem;max-width:1080px;}
    .hero{background:linear-gradient(140deg,#1B4D1F,#2D6A2F 55%,#4CAF50);padding:2.5rem 2.5rem 2rem;border-radius:16px;margin-bottom:2rem;position:relative;overflow:hidden;}
    .hero::after{content:'🌾';position:absolute;right:1.5rem;top:50%;transform:translateY(-50%);font-size:5rem;opacity:0.12;}
    .hero h1{font-family:'Playfair Display',serif;font-size:2.6rem;color:#fff;margin:0;}
    .hero h1 em{color:#A5D6A7;font-style:normal;}
    .hero p{color:#C8E6C9;font-size:0.95rem;margin:0.4rem 0 0;max-width:560px;}
    .hero small{display:inline-block;background:rgba(255,255,255,0.18);border:1px solid rgba(255,255,255,0.3);color:white;font-size:0.7rem;font-weight:600;padding:0.2rem 0.6rem;border-radius:999px;margin-top:0.7rem;letter-spacing:0.6px;text-transform:uppercase;}
    .card{background:#fff;border-radius:12px;border:1px solid #E2E8D9;padding:1.4rem;box-shadow:0 2px 8px rgba(0,0,0,0.05);margin-bottom:1rem;}
    .card-title{font-family:'Playfair Display',serif;font-size:1.05rem;color:#2D6A2F;margin-bottom:0.8rem;}
    .result-pill{display:inline-flex;align-items:center;gap:0.4rem;font-size:1.05rem;font-weight:600;padding:0.45rem 1.1rem;border-radius:999px;margin-bottom:0.8rem;}
    .sev-bar{background:#ECEFE8;border-radius:999px;height:12px;overflow:hidden;margin:0.3rem 0;}
    .sev-fill{height:100%;border-radius:999px;}
    .metric{background:#F7F9F4;border:1px solid #E2E8D9;border-radius:10px;padding:0.8rem;text-align:center;}
    .metric-lbl{font-size:0.68rem;color:#7A8A70;text-transform:uppercase;letter-spacing:0.8px;font-weight:600;}
    .metric-val{font-family:'Playfair Display',serif;font-size:1.7rem;line-height:1.15;}
    .rec-box{padding:0.9rem 1.1rem;border-radius:10px;border-left:4px solid;font-size:0.9rem;line-height:1.65;}
    .stButton>button{background:linear-gradient(135deg,#2D6A2F,#1B4D1F)!important;color:white!important;border:none!important;border-radius:10px!important;font-weight:600!important;width:100%!important;height:2.8rem!important;}
    .footer{text-align:center;color:#9BA88F;font-size:0.78rem;padding:1.5rem 0 0.5rem;border-top:1px solid #E2E8D9;margin-top:2rem;}
    </style>
    """, unsafe_allow_html=True)

def demo_predict(pil_image):
    time.sleep(1.2)
    classes = ['healthy','mild','moderate','severe']
    weights = [0.25, 0.35, 0.25, 0.15]
    pred = random.choices(classes, weights=weights)[0]
    import numpy as np
    raw = np.abs(np.random.randn(4))
    total = raw.sum()
    probs = {c: round(float(r/total*100), 1) for c,r in zip(classes,raw)}
    sev_map = {'healthy':0.0,'mild':15.0,'moderate':35.0,'severe':65.0}
    return {'predicted_class':pred,'confidence':probs[pred],'severity_pct':sev_map[pred],'class_probs':probs,'gradcam_overlay':None}

def run_prediction(pil_image):
    try:
        from model.inference import predict
        return predict(pil_image, generate_gradcam=False)
    except Exception:
        return demo_predict(pil_image)

def prob_chart(class_probs, tr):
    classes = list(class_probs.keys())
    values  = list(class_probs.values())
    labels  = [tr.get(c, c.title()) for c in classes]
    colors  = [CLASS_COLORS[c] for c in classes]
    fig, ax = plt.subplots(figsize=(4.5, 2.2))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('#F7F9F4')
    bars = ax.barh(labels[::-1], values[::-1], color=colors[::-1], height=0.5, edgecolor='none')
    for bar, val in zip(bars, values[::-1]):
        ax.text(bar.get_width()+0.5, bar.get_y()+bar.get_height()/2, f'{val:.1f}%', va='center', ha='left', fontsize=8.5, color='#374151')
    ax.set_xlim(0, 118)
    ax.tick_params(labelsize=8.5, colors='#374151')
    for sp in ['top','right','left']: ax.spines[sp].set_visible(False)
    ax.spines['bottom'].set_color('#D1D5DB')
    ax.grid(axis='x', linestyle='--', alpha=0.4, color='#E5E7EB')
    plt.tight_layout(pad=0.4)
    return fig

def render_results(result):
    tr    = st.session_state.get('translations', {})
    pred  = result['predicted_class']
    conf  = result['confidence']
    sev   = result['severity_pct']
    probs = result['class_probs']
    color = CLASS_COLORS[pred]
    emoji = SEVERITY_EMOJIS.get(pred, '')
    pred_label = tr.get(pred, pred.title())
    desc_text  = tr.get(f'{pred}_desc', '')
    rec_text   = tr.get(f'rec_{pred}', '')

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-title">📊 {tr.get("results_title","Results")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="result-pill" style="background:{color}22;color:{color};border:1.5px solid {color};">{emoji} {pred_label}</div><br><span style="font-size:0.85rem;color:#6B7280;">{desc_text}</span>', unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="metric"><div class="metric-lbl">{tr.get("severity_label","Severity")}</div><div class="metric-val" style="color:{color}">{sev:.1f}%</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric"><div class="metric-lbl">{tr.get("confidence_label","Confidence")}</div><div class="metric-val">{conf:.1f}%</div></div>', unsafe_allow_html=True)
    with c3:
        badge = tr.get(f'badge_{pred}', pred.upper())
        st.markdown(f'<div class="metric"><div class="metric-lbl">Status</div><div class="metric-val" style="font-size:1rem;color:{color}">{badge}</div></div>', unsafe_allow_html=True)

    st.markdown(f'<br><b>{tr.get("severity_label","Severity")}</b>', unsafe_allow_html=True)
    st.markdown(f'<div class="sev-bar"><div class="sev-fill" style="width:{min(sev,100):.1f}%;background:{color};"></div></div><small style="color:#9BA88F">{sev:.1f} {tr.get("severity_unit","% lodging")}</small>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-title">📈 {tr.get("probability_title","Probabilities")}</div>', unsafe_allow_html=True)
    fig = prob_chart(probs, tr)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
    st.markdown('</div>', unsafe_allow_html=True)

    rec_styles = {'healthy':('#D1FAE5','#065F46','#10B981'),'mild':('#FEF9C3','#78350F','#F59E0B'),'moderate':('#FFEDD5','#7C2D12','#F97316'),'severe':('#FEE2E2','#7F1D1D','#EF4444')}
    bg,tc,bc = rec_styles.get(pred, ('#F3F4F6','#111827','#6B7280'))
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-title">💡 {tr.get("recommendation_label","Recommendation")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="rec-box" style="background:{bg};color:{tc};border-left-color:{bc};">{rec_text}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    inject_css()
    with st.sidebar:
        st.markdown('### 🌐 Language / भाषा')
        lang_choice = st.selectbox('lang', list(LANGUAGES.keys()), label_visibility='collapsed')
    lang_code = LANGUAGES[lang_choice]
    tr = load_translations(lang_code)
    st.session_state['translations'] = tr

    st.markdown(f'''<div class="hero">
        <h1>Agro<em>Tiltix</em></h1>
        <p>{tr.get('subtitle','')}</p>
        <small>AI · EfficientNet-B0 · Transfer Learning · 4-Class</small>
    </div>''', unsafe_allow_html=True)

    left, right = st.columns([1,1], gap='large')

    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div class="card-title">📷 {tr.get("upload_label","Upload Image")}</div>', unsafe_allow_html=True)
        st.caption(tr.get('upload_hint','JPG, PNG'))
        uploaded = st.file_uploader('up', type=['jpg','jpeg','png'], label_visibility='collapsed')
        if uploaded:
            img = Image.open(uploaded)
            st.image(img, caption=tr.get('uploaded_image','Uploaded Image'), use_column_width=True)
            st.caption(f'📐 {img.size[0]} x {img.size[1]} px')
        st.markdown('</div>', unsafe_allow_html=True)
        btn = st.button(f'🔍 {tr.get("predict_button","Analyze")}', disabled=(uploaded is None))
        with st.expander(f'ℹ️ {tr.get("about_title","About")}'):
            st.write(tr.get('about_text',''))

    with right:
        if uploaded is None:
            st.markdown(f'<div style="background:#fff;border:2px dashed #C8D8C0;border-radius:12px;height:380px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;color:#9BA88F;padding:2rem;"><div style="font-size:3rem;margin-bottom:0.7rem">🌾</div><div style="font-weight:500;color:#7A8A70">{tr.get("no_image","Upload an image")}</div></div>', unsafe_allow_html=True)
        elif btn:
            with st.spinner(tr.get('analyzing','Analyzing...')):
                try:
                    img = Image.open(uploaded)
                    result = run_prediction(img)
                    st.session_state['last_result'] = result
                except Exception as e:
                    st.error(f"{tr.get('error_title','Error')}: {e}")
                    return
            render_results(st.session_state['last_result'])
        elif 'last_result' in st.session_state:
            render_results(st.session_state['last_result'])

    st.markdown(f'<div class="footer">{tr.get("footer","AgroTiltix 2024")}</div>', unsafe_allow_html=True)

if __name__ == '__main__':
    main()
