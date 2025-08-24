# pages/1_About.py

import streamlit as st

st.set_page_config(page_title="About · Nurse Next AI", page_icon="🩺", layout="wide")

st.markdown("## 🩺 About **Nurse Next AI**")
st.caption(
    "This tool provides general educational health information only. "
    "It is **NOT** a substitute for professional medical advice. "
    "For emergencies, call your local emergency number."
)

st.markdown("---")

st.markdown("### What this app does")
st.markdown(
    """
- A simple, lightweight Streamlit chatbot UI with a floating nurse icon.
- **Guardrails**: detects emergencies (e.g., chest pain, stroke signs, suicidal ideation) and shows a safety message; blocks medication dosing/prescriptions.
- **Model fallback + retries**: uses your configured model and retries transient errors with backoff.
- **No PII storage**: chat state lives only in your session. Nothing is stored server-side by this app.
"""
)

st.markdown("---")

st.markdown("### Provider & model selection (Groq first)")
st.write(
    """
This app is configured to run **primarily on Groq** for fast, generous free-tier access.  
If Groq isn’t configured, it can fall back to **OpenAI** or **OpenRouter** (whichever keys are present).
    """
)

st.markdown(
    """
**Resolution order:**
1. **Groq** *(recommended primary)*  
   - Secret: `GROQ_API_KEY`  
   - Default model: `llama3-70b-8192` (or your `GROQ_MODEL`)

2. **OpenAI** *(optional)*  
   - Secret: `OPENAI_API_KEY`  
   - Default model: `gpt-4o-mini` (or your `OPENAI_MODEL`)

3. **OpenRouter** *(optional)*  
   - Secret: `OPENROUTER_API_KEY`  
   - Default model: `openrouter/auto` (or your `OPENROUTER_MODEL`)
"""
)

with st.expander("🔐 Set secrets on Streamlit Cloud (recommended)"):
    st.markdown(
        """
Go to **⋯ → Settings → Secrets** and add (TOML format):

```toml
# Primary (Groq)
AI_PROVIDER      = "groq"
GROQ_API_KEY     = "gsk_..."
GROQ_MODEL       = "llama3-70b-8192"   # Optional override

# Optional: OpenAI fallback
OPENAI_API_KEY   = "sk-..."
OPENAI_MODEL     = "gpt-4o-mini"

# Optional: OpenRouter fallback
OPENROUTER_API_KEY = "or_..."
OPENROUTER_MODEL   = "openrouter/auto"
"""
    )