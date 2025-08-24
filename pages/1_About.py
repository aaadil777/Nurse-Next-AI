# pages/1_About.py

import streamlit as st

st.set_page_config(page_title="About · Nurse Next AI", page_icon="🩺", layout="wide")

st.markdown("## 🩺 About **Nurse Next AI**")
st.caption(
    "This tool is here to share general health education in a simple, friendly way. "
    "It is **NOT** a substitute for professional medical advice. "
    "For emergencies, always call your local emergency number."
)

st.markdown("---")

st.markdown("### What this app does")
st.markdown(
    """
- 💬 Chat with a **virtual nurse assistant** inside an easy-to-use panel.  
- 🚨 Built-in **safety checks**: if you mention emergency symptoms (like chest pain or stroke signs), it will immediately suggest calling for help.  
- 🛑 Protects you by **blocking medical prescriptions or dosages** — this app is for learning, not treatment.  
- 🔄 **Smart reliability**: if one AI service is too busy, it can automatically switch to another in the background.  
- 🔒 **Private by design**: your questions and answers only stay in your session — nothing is saved or shared.  
"""
)

st.markdown("---")

st.markdown("### How the app picks a model")
st.markdown(
    """
To keep the chat smooth and responsive, Nurse Next AI connects to different AI providers.  
It will always try the most reliable option first, and switch if needed:

1. **Groq (main choice)**  
   - Fast, free-tier friendly.  
   - Default model: `llama3-70b-8192` (unless you change it).  

2. **OpenAI (backup option)**  
   - Uses popular models like `gpt-4o-mini`.  

3. **OpenRouter (extra backup)**  
   - Can route to other models such as Google’s Gemini.  

> Most of the time, you don’t need to worry about this — the app picks the best available option for you.
"""
)

with st.expander("🔐 Want to connect your own AI account? (advanced users)"):
    st.markdown(
        """
If you’d like to connect your own AI provider keys (optional), go to  
**⋯ → Settings → Secrets** in Streamlit and paste them in TOML format:

```toml
# Groq (main)
AI_PROVIDER  = "groq"
GROQ_API_KEY = "gsk_..."
GROQ_MODEL   = "llama3-70b-8192"

# OpenAI (optional fallback)
OPENAI_API_KEY = "sk-..."
OPENAI_MODEL   = "gpt-4o-mini"

# OpenRouter (optional fallback)
OPENROUTER_API_KEY = "or_..."
OPENROUTER_MODEL   = "openrouter/auto"
"""
    )