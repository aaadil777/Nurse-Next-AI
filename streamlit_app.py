import os, re
import streamlit as st
from openai import OpenAI

# ---------- Config ----------
st.set_page_config(page_title="Nurse Next AI (Educational)", page_icon="🩺", layout="centered")
st.title("🩺 Nurse Next AI (Educational)")
st.caption("This tool provides general educational health information only. It is NOT a substitute for professional medical advice. For emergencies, call your local emergency number.")

# Get API key (Streamlit Cloud: set in App → Settings → Secrets)
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
if not OPENAI_API_KEY:
    st.error("OPENAI_API_KEY not found. Add it to Streamlit Secrets or your environment.")
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)

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

EMERGENCY_MSG = ("If you’re experiencing symptoms like chest pain, trouble breathing, stroke signs, severe bleeding, "
                 "anaphylaxis, or thoughts of self-harm, call your local emergency number immediately. "
                 "I can only provide general educational information, not medical advice.")
REFUSAL_MSG = ("I can’t help with that request. I’m not a clinician and can’t provide dosing, prescriptions, "
               "or controlled-substance guidance. I can share general educational information instead.")

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
- If the user reports emergency red flags (chest pain, trouble breathing, stroke signs, suicidal ideation, anaphylaxis, severe bleeding), advise calling emergency services immediately.
- Be concise, structured (bullets, short paragraphs), and clear.
- If uncertain, say so and suggest safe next steps and when to seek care.
- Do not invent statistics or guidelines; keep to general principles unless the user provides a source.
- Keep replies around 200 words unless the user asks for more detail.
- End with a brief, actionable next step when possible.
"""

# ---------- Sidebar options ----------
with st.sidebar:
    st.header("Settings")
    model = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o"], index=0)
    temperature = st.slider("Creativity (temperature)", 0.0, 1.0, 0.2, 0.05)
    st.markdown("---")
    st.markdown("**Privacy:** Avoid entering names, addresses, or other personal identifiers.")

# ---------- Chat State ----------
if "history" not in st.session_state:
    st.session_state.history = [
        {"role":"assistant", "content":"Hi! I can share general health information. What can I help you with today?"}
    ]

# Render history
for m in st.session_state.history:
    with st.chat_message(m["role"]):
        st.write(m["content"])

# Input box
user_input = st.chat_input("Type your question…")
if user_input:
    # Append user message
    st.session_state.history.append({"role":"user","content":user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Guardrails
    if needs_emergency_escalation(user_input):
        reply = EMERGENCY_MSG
    elif needs_refusal(user_input):
        reply = REFUSAL_MSG
    else:
        messages = [{"role":"system","content": SYSTEM_PROMPT}] + st.session_state.history[-10:]
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature
            )
            reply = resp.choices[0].message.content
        except Exception as e:
            reply = f"Upstream model error: {e}"

    # Show reply
    st.session_state.history.append({"role":"assistant","content":reply})
    with st.chat_message("assistant"):
        st.write(reply)
