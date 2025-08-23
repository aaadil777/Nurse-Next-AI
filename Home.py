# Home.py
import os, re, time, random
import streamlit as st
from openai import OpenAI
from openai import AuthenticationError, RateLimitError, APIError

# ──────────────────────────────────────────────────────────────────────────────
# Page setup
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Nurse Next AI", page_icon="🩺", layout="wide")

# ──────────────────────────────────────────────────────────────────────────────
# Secrets / API key
# Works with Streamlit Secrets or a local env var
# ──────────────────────────────────────────────────────────────────────────────
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.error(
        "OPENAI_API_KEY not found. Add it in Streamlit Secrets (⋯ → Settings → Secrets) "
        "or as an environment variable."
    )
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)

# Preferred model order (first available wins). You can override with OPENAI_MODEL env var.
MODEL_OVERRIDES = [
    os.getenv("OPENAI_MODEL"),                 # if user provided
    "gpt-4o-mini-2024-07-18",                  # newer mini endpoint
    "gpt-3.5-turbo",                           # resilient fallback
]
MODEL_CANDIDATES = [m for m in MODEL_OVERRIDES if m]  # remove None

# ──────────────────────────────────────────────────────────────────────────────
# Styles (we will render floating UI only when needed, so no phantom white box)
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
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

/* Chat panel (raised too) */
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
.nurse-user .nurse-bubble { background:#E6FFFA; color:#0F766E; }
.nurse-bot  .nurse-bubble { background:#F7F7F9; }

.nurse-footer { padding: 10px; border-top: 1px solid #eee; background:#fff; }
.nurse-note { font-size: 12px; color:#4b5563; margin-top:6px;}
</style>
""",
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────────
# Guardrails
# ──────────────────────────────────────────────────────────────────────────────
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

# ──────────────────────────────────────────────────────────────────────────────
# Header
# ──────────────────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("## 🩺 **Nurse Next AI**")
    st.caption(
        "This tool provides general educational health information only. "
        "It is NOT a substitute for professional medical advice. For emergencies, call your local emergency number."
    )

# ──────────────────────────────────────────────────────────────────────────────
# Chat state & sidebar toggle
# ──────────────────────────────────────────────────────────────────────────────
if "chat_open" not in st.session_state:
    st.session_state.chat_open = True

if "history" not in st.session_state:
    st.session_state.history = [
        {
            "role": "assistant",
            "content": "Hi! I can share general health information. What can I help you with today?",
        }
    ]

st.sidebar.markdown("### Chat")
if st.sidebar.button("Toggle chat", use_container_width=True):
    st.session_state.chat_open = not st.session_state.chat_open

# ──────────────────────────────────────────────────────────────────────────────
# Model call with retry/backoff + multi-model fallback
# ──────────────────────────────────────────────────────────────────────────────
def call_model(messages):
    # Try models in order (override → 4o-mini 2024-07-18 → 3.5-turbo)
    last_error_text = None

    for model in MODEL_CANDIDATES:
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                resp = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.2,
                )
                return resp.choices[0].message.content
            except AuthenticationError:
                return (
                    "Your OpenAI API key seems invalid or missing. "
                    "Open the menu (⋯ → Settings → Secrets) and set `OPENAI_API_KEY`, then rerun."
                )
            except RateLimitError as e:
                last_error_text = f"Rate limit on {model}: {e}"
                if attempt < max_attempts - 1:
                    time.sleep((2 ** attempt) + random.uniform(0, 0.5))
                    continue
                # break inner loop to try next model
                break
            except APIError as e:
                # transient server errors: retry once or twice
                last_error_text = f"API error on {model}: {getattr(e, 'message', e)}"
                if attempt < max_attempts - 1:
                    time.sleep(1.5)
                    continue
                break
            except Exception as e:
                # unknown error: no retry for this model, try next model
                last_error_text = f"Unexpected error on {model}: {e}"
                break

    # If we get here, all models failed
    return last_error_text or "Upstream model error: all model attempts failed."

# ──────────────────────────────────────────────────────────────────────────────
# Floating UI — render only when chat is open (prevents stray white box)
# ──────────────────────────────────────────────────────────────────────────────
if st.session_state.chat_open:
    # Floating action button
    st.markdown('<div id="nurse-fab">👩‍⚕️</div>', unsafe_allow_html=True)

    # Chat panel
    st.markdown('<div id="nurse-panel">', unsafe_allow_html=True)
    st.markdown(
        '<div class="nurse-header"><div class="avatar">👩‍⚕️</div> Nurse Next</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="nurse-body">', unsafe_allow_html=True)

    # Render chat history
    for m in st.session_state.history[-50:]:
        who = "nurse-user" if m["role"] == "user" else "nurse-bot"
        st.markdown(
            f'<div class="nurse-msg {who}"><div class="nurse-bubble">{m["content"]}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)  # close body
    st.markdown('<div class="nurse-footer">', unsafe_allow_html=True)

    user_input = st.chat_input("Type your question…")
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

    st.markdown(
        '<div class="nurse-note">This chatbot is for general education only.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("</div></div>", unsafe_allow_html=True)  # close footer & panel
else:
    # If chat is toggled off, ensure no phantom elements remain
    st.markdown(
        "<style>#nurse-panel, #nurse-fab { display: none !important; }</style>",
        unsafe_allow_html=True,
    )
