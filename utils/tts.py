"""
tts.py - Vernacular Voice Output for FarmRakshak
Uses the browser's built-in Web Speech API (speechSynthesis).
Works offline. Supports Hindi (hi-IN) and Marathi (mr-IN).
No external TTS library needed - runs entirely in the browser.
"""

import streamlit.components.v1 as components


# Language code to BCP-47 locale mapping for speechSynthesis
LANG_VOICE_MAP = {
    "en": "en-IN",   # Indian English accent
    "hi": "hi-IN",   # Hindi
    "mr": "mr-IN",   # Marathi
}


def build_speech_text(tr: dict, predicted_class: str, severity_pct: float,
                       confidence: float, lang_code: str) -> str:
    """
    Builds the spoken sentence from translation keys.
    Combines status, severity, and recommendation into a natural speech string.
    """
    pred_label = tr.get(predicted_class, predicted_class)
    rec_text   = tr.get(f"rec_{predicted_class}", "")
    sev_label  = tr.get("severity_label", "Severity")
    conf_label = tr.get("confidence_label", "Confidence")

    if lang_code == "en":
        text = (
            f"Crop analysis complete. "
            f"Status: {pred_label}. "
            f"{sev_label}: {severity_pct:.0f} percent. "
            f"{conf_label}: {confidence:.0f} percent. "
            f"Recommendation: {rec_text}"
        )
    elif lang_code == "hi":
        text = (
            f"\u092b\u0938\u0932 \u0935\u093f\u0936\u094d\u0932\u0947\u0937\u0923 \u092a\u0942\u0930\u093e \u0939\u0941\u0906. "
            f"\u0938\u094d\u0925\u093f\u0924\u093f: {pred_label}. "
            f"\u0917\u0902\u092d\u0940\u0930\u0924\u093e: {severity_pct:.0f} \u092a\u094d\u0930\u0924\u093f\u0936\u0924. "
            f"{rec_text}"
        )
    elif lang_code == "mr":
        text = (
            f"\u092a\u093f\u0915 \u0935\u093f\u0936\u094d\u0932\u0947\u0937\u0923 \u092a\u0942\u0930\u094d\u0923 \u091d\u093e\u0932\u0947. "
            f"\u0938\u094d\u0925\u093f\u0924\u0940: {pred_label}. "
            f"\u0924\u0940\u0935\u094d\u0930\u0924\u093e: {severity_pct:.0f} \u091f\u0915\u094d\u0915\u0947. "
            f"{rec_text}"
        )
    else:
        text = f"Status: {pred_label}. Severity: {severity_pct:.0f}%. {rec_text}"

    return text


def render_tts_button(speech_text: str, lang_code: str, button_label: str = "\U0001f50a Speak Result"):
    """
    Renders a TTS button using the Web Speech API via injected HTML/JS.
    The browser speaks the text aloud in the appropriate language voice.

    Args:
        speech_text:  Text to speak
        lang_code:    Language code (en, hi, mr)
        button_label: Button display text
    """
    voice_locale = LANG_VOICE_MAP.get(lang_code, "en-IN")

    # Escape single quotes in text for JS safety
    safe_text = speech_text.replace("\\", "").replace("'", "\'").replace('"', "\'")

    html_code = f"""
    <div style="margin: 0.5rem 0;">
        <button onclick="speakResult()" style="
            background: linear-gradient(135deg, #1B5E20, #2E7D32);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.55rem 1.3rem;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 0.4rem;
            box-shadow: 0 2px 8px rgba(27,94,32,0.3);
            transition: all 0.2s ease;
        " onmouseover="this.style.opacity=0.85" onmouseout="this.style.opacity=1">
            &#128266; {button_label}
        </button>
        <div id="speech-status" style="font-size:0.75rem; color:#6B7280; margin-top:0.3rem; min-height:1rem;"></div>
    </div>

    <script>
    function speakResult() {{
        if (!window.speechSynthesis) {{
            document.getElementById("speech-status").innerText = "\u26a0 TTS not supported in this browser.";
            return;
        }}
        // Cancel any ongoing speech
        window.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(`{safe_text}`);
        utterance.lang = "{voice_locale}";
        utterance.rate = 0.88;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;

        // Prefer a native voice for the language
        const voices = window.speechSynthesis.getVoices();
        const preferred = voices.find(v => v.lang === "{voice_locale}");
        if (preferred) utterance.voice = preferred;

        utterance.onstart = () => {{
            document.getElementById("speech-status").innerText = "\U0001f4ac Speaking...";
        }};
        utterance.onend = () => {{
            document.getElementById("speech-status").innerText = "\u2714 Done";
            setTimeout(() => document.getElementById("speech-status").innerText = "", 2000);
        }};
        utterance.onerror = (e) => {{
            document.getElementById("speech-status").innerText = "\u26a0 Speech error: " + e.error;
        }};

        window.speechSynthesis.speak(utterance);
    }}

    // Preload voices (Chrome lazy-loads them)
    if (window.speechSynthesis.onvoiceschanged !== undefined) {{
        window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
    }}
    </script>
    """
    components.html(html_code, height=90)
