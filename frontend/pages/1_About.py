# pages/1_About.py
import streamlit as st

st.set_page_config(page_title="About • Nurse Next AI", page_icon="🩺", layout="wide")

# ---- Header ----
st.markdown("## 🩺 About **Nurse Next AI**")
st.caption(
    "Educational health chatbot. This tool does **not** replace professional medical care. "
    "If you have an emergency, call your local emergency number immediately."
)

# ---- What it is ----
st.markdown("### What is this?")
st.write(
    """
**Nurse Next AI** is a simple, empathetic chat interface that provides **general, educational health
information**. It does **not** diagnose, prescribe medication, or determine drug doses.  
It’s built with **Streamlit** (UI) and **OpenAI** models (responses), with basic **guardrails** for safety.
"""
)

# ---- How to use ----
st.markdown("### How do I use it?")
st.write(
    """
1. Type a question in the chat box on the home page.  
2. You’ll get a short, structured reply with general information and suggested next steps.  
3. If your message contains urgent red-flag symptoms, you’ll see a prompt to **seek emergency care**.  
4. For personal medical advice, always consult a licensed professional.
"""
)

# ---- Safety & limitations ----
with st.expander("Safety & Limitations"):
    st.write(
        """
- **Not a doctor:** Replies are educational only; no prescriptions, no dosing, and no medical decisions.
- **Guardrails:** Emergency and disallowed topics trigger a safe response (e.g., “call emergency services” or “can’t help with that”).
- **Uncertainty:** If unsure, the assistant should say so and suggest safe next steps.
"""
    )

# ---- Data handling ----
with st.expander("Data & Privacy"):
    st.write(
        """
- This demo sends your prompt to the OpenAI API to generate a response.
- Do **not** share personal identifiers or sensitive medical details.
- Your API key (if set) is stored as a **Streamlit Secret** and is not committed to the repository.
"""
    )

# ---- Tips ----
st.markdown("### Tips for better answers")
st.write(
    """
- Ask **one thing at a time** with relevant background (age range, general context).  
- If you want more detail, say “provide more detail” or ask for **pros/cons** or **next steps**.
- You can switch languages; short, clear wording helps.
"""
)

# ---- Troubleshooting ----
with st.expander("Troubleshooting"):
    st.write(
        """
- **“API key not found”**: Add your key in *⋯ → Settings → Secrets* as `OPENAI_API_KEY`.
- **Rate-limited**: The app automatically retries briefly; if it persists, wait a minute and try again.
- **Blank or odd UI**: Refresh the page. If the floating chat overlaps controls, it auto-adjusts its position.
"""
    )

# ---- Tech stack ----
st.markdown("### Tech stack")
st.write(
    """
- **UI:** Streamlit  
- **Model:** OpenAI `gpt-4o-mini` (configurable)  
- **Safety:** Simple pattern-based guardrails for emergencies and refusals  
"""
)

st.divider()
st.write("Version: **v1.0**  •  Maintainer: *Nurse Next AI*")
