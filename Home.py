# Home.py
import os, re, time, random
import streamlit as st
from openai import OpenAI
from openai import AuthenticationError, RateLimitError, APIError

# ---------- Page setup ----------
st.set_page_config(page_title="Nurse Next AI", page_icon="🩺", layout="wide")

# ---------- Provider selection ----------
# AI_PROVIDER in { "openai", "groq", "openrouter" }
PROVIDER = (st.secrets.get("AI_PROVIDER") or os.getenv("AI_PROVIDER") or "openai").lower()

def make_client_and_model():
    """
    Creates a single OpenAI-compatible client for the selected provider
    and returns (client, model_name).
    """
    app_url = st.secrets.get("APP_URL") or os.getenv("APP_URL") or "https://nurse-next-ai.streamlit.app"

    if PROVIDER == "groq":
        # Groq: OpenAI-compatible endpoint
        groq_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
        if not groq_key:
            st.error("GROQ_API_KEY not found. Add it in Streamlit Secrets.")
            st.stop()
        base_url = "https://api.groq.com/openai/v1"
        model = st.secrets.get("GROQ_MODEL") or os.getenv("GROQ_MODEL") or "llama3-70b-8192"
        client = OpenAI(
            api_key=groq_key,
            base_url=base_url,
            # headers not required for Groq, but allowed
        )
        return client, model

    if PROVIDER == "openrouter":
        # OpenRouter: OpenAI-compatible endpoint
        or_key = st.secrets.get("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        if not or_key:
            st.error("OPENROUTER_API_KEY not found. Add it in Streamlit Secrets.")
            st.stop()
        base_url = "https://openrouter.ai/api/v1"
        model = st.secrets.get("OPENROUTER_MODEL") or os.getenv("OPENROUTER_MODEL") or "openrouter/auto"
        # OpenRouter encourages including referer + title
        client = OpenAI(
            api_key=or_key,
            base_url=base_url,
            default_headers={
                "HTTP-Referer": app_url,
                "X-Title": "Nurse Next AI",
            },
        )
        return client, model

    # Default: OpenAI
    oa_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not oa_key:
        st.error(
            "OPENAI_API_KEY not found. Set AI_PROVIDER to 'groq' or 'openrouter' with an API key, "
            "or add your OpenAI key in Streamlit Secrets."
        )
        st.stop()
    model = st.secrets.get("OPENAI_MODEL") or os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
    client = OpenAI(api_key=oa_key)
    return client, model

client, MODEL = make_client_and_model()

# ---------- Styles ----------
# Hide the floating side-panel (the big white rectangle) by default.
USE_FLOATING_PANEL = False  # set True if you want the floating panel back

st.markdown("""
<style>
/* Floating chat button (raised to avoid Streamlit Cloud controls) */
#nurse-fab {
  position: fixed;
  right: 20px; bottom: 96px;
  width: 56px; height: 56px;
  background: linear-gradient(135deg,#0F766E,#14B8A6);
  border-radius: 50%;
  box-shadow: 0 8px 24px rgba(0,0,0,.15);
  display: flex; align-items: center; justify-content: center;
  color: #fff; font-size: 28px; cursor: pointer; z-index: 1000;
}

/* Chat panel (disabled unless USE_FLOATING_PANEL=True) */
#nurse-panel {
  position: fixed;
  right: 20px; bottom: 166px;
  width: 420px; max-width: 92vw; height: 520px;
  background: #ffffff; border-radius: 14px;
  box-shadow: 0 12px 36px rgba(0,0,0,.18);
  overflow: hidden; z-index: 999;
  border: 1px solid rgba(15,118,110,.10);
}
.nurse-header {
  background: linear-gradient(135deg,#0F766E,#14B8A6);
  color: #fff; padding: 10px 14px; font-weight: 700;
  display: flex; align-items: center; gap: 8px;
}
.nurse-header .avatar {
  width: 26px; height: 26px; border-radius: 50%;
  background: #ffffff22; display:flex; align-items:center; justify-content:center;
}
.nurse-body { padding: 12px 14px; height: 360px; overflow-y: auto; }
.nurse-msg { margin: 8px 0; }
.nurse-user   { text-align: right; }
.nurse-bubble {
  display: inline-block; padding: 10px 12px; border-radius: 12px;
  max-width: 95%;
}
.nurse-user .nurse-bubble   { background:#E6FFFA; color:#0F766E; }
.nurse-bot  .nurse-bubble   { background:#F7F7F9; }
.nurse-footer { padding: 10px; border-top: 1px solid #eee; background:#fff; }
.nurse-note { font-size: 12px; color:#4b5563; margin-top:6px;}
</style>
""", unsafe_allow_html=True)

if not USE_FLOATING_PANEL:
    # Nuke the white box if CSS somehow renders it
    st.markdown("<style>#nurse-panel{display:none!important;}</style>", unsafe_allow_html=True)

# ---------- Guardrails ----------
EMERGENCY_PATTERNS = [
    r"\b(chest pain|pressure in chest|tightness in chest)\b",
    r"\b(trouble breathing|shortness of breath|can't breathe|cannot breathe)\b",
    r"\b(stroke|face droop|slurred speech|one[- ]sided weakness|sudden numbness)\b",
    r"\b(severe bleeding|bleeding won't stop|profuse bleeding)\b",
    r"\b(suicidal|kill myself|end my life|self[- ]harm|harm myself)\b",
    r"\b(anaphylaxis|throat closing|severe allergic reaction)\b",
]
BANNED_PATTERNS = [
    r"\b(prescribe|prescription|controlled substances?)\b",
    r"\b(dose|dosage)\b.*\b(baby|infant|newborn|pregnan\w*)",
]
EMERGENCY_MSG = (
    "If you’re experiencing symptoms like chest pain, trouble breathing, stroke signs, "
    "severe bleeding, anaphylaxis, or thoughts of self-harm, call your local emergency "
    "number immediately. I can only provide general educational information, not medical advice."
)
REFUSAL_MSG = (
    "I can’t help with that request. I’m not a clinician and can’t provide dosing, prescriptions, "
    "or controlled-substance guidance. I can share general educational information instead."
)

def needs_emergency_escalation(text: str) -> bool:
    t = (text or "").lower()
    return any(re.search(p, t) for p in EMERGENCY_PATTERNS)

def needs_refusal(text: str) -> bool:
    t = (text or "").lower()
    return any(re.search(p, t) for p in BANNED_PATTERNS)

SYSTEM_PROMPT = """You are an empathetic health information assistant.
- You are NOT a doctor; provide general education only.
- Do not provide definitive diagnoses or personalized medication dosing.
- Encourage seeing a licensed professional for personal medical advice.
- If the user reports emergency red flags (chest pain, trouble breathing, stroke signs, suicidal ideation, anaphylaxis, severe bleeding),
  advise calling emergency services immediately.
- Be concise, structured (bullets, short paragraphs), and clear.
- If uncertain, say so and suggest safe next steps and when to seek care.
- Do not invent statistics or guidelines; keep to general principles unless the user provides a source.
- Keep replies ~200 words unless the user asks for more detail.
- End with a brief, actionable next step when possible.
"""

# ---------- Header ----------
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.markdown("## 🩺 **Nurse Next AI**")
    st.caption("This tool provides general educational health information only. It is NOT a substitute for professional medical advice. For emergencies, call your local emergency number.")

# ---------- Sidebar toggle ----------
if "chat_open" not in st.session_state:
    st.session_state.chat_open = True
st.sidebar.markdown("### Chat")
if st.sidebar.button("Toggle chat", use_container_width=True):
    st.session_state.chat_open = not st.session_state.chat_open

# ---------- Chat state ----------
if "history" not in st.session_state:
    st.session_state.history = [
        {"role": "assistant", "content": "Hi! I can share general health information. What can I help you with today?"}
    ]

# ---------- Helper: call model with retry/backoff ----------
def call_model(messages):
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.2,
            )
            return resp.choices[0].message.content
        except AuthenticationError:
            return (
                f"Your {PROVIDER} API key seems invalid or missing. "
                "Open the menu (⋯ → Settings → Secrets), set the correct key, then rerun."
            )
        except RateLimitError:
            if attempt < max_attempts - 1:
                time.sleep((2 ** attempt) + random.uniform(0, 0.5))
                continue
            return (
                f"Rate limit on **{MODEL}**. "
                "If this says `insufficient_quota`, add credits to your API project or switch provider in Secrets."
            )
        except APIError as e:
            if attempt < max_attempts - 1:
                time.sleep(1.5)
                continue
            return f"Upstream model error: {getattr(e, 'message', str(e))}"
        except Exception as e:
            return f"Upstream model error: {e}"

# ---------- Floating button (panel disabled by default) ----------
st.markdown('<div id="nurse-fab">👩‍⚕️</div>', unsafe_allow_html=True)

# ---------- Main-page chat ----------
# (This is the one you see — the floating panel is disabled to avoid the white box.)
st.divider()
user_input = st.chat_input("Type your question…")

# Render history
for m in st.session_state.history[-50:]:
    with st.chat_message("user" if m["role"] == "user" else "assistant"):
        st.markdown(m["content"])

if user_input:
    st.session_state.history.append({"role": "user", "content": user_input})
    if needs_emergency_escalation(user_input):
        reply = EMERGENCY_MSG
    elif needs_refusal(user_input):
        reply = REFUSAL_MSG
    else:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.history[-10:]
        reply = call_model(messages)
    st.session_state.history.append({"role": "assistant", "content": reply})
    st.rerun()

st.caption("This chatbot is for general education only.")
