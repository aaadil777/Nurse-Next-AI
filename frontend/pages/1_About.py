import streamlit as st

st.title("About Nurse Next AI")
st.write("""
**Nurse Next AI** is an educational health assistant. It explains common symptoms, self-care basics,
and when to seek care — in plain language.

**Important:**
- It is **not** a doctor and does **not** replace professional medical advice.
- For **emergencies** (chest pain, trouble breathing, severe bleeding, stroke signs, anaphylaxis, or thoughts of self-harm),
  call your local emergency number immediately.
- We do not store PHI by default. Avoid entering names, addresses, or other identifiers.

**How to use:**
1. Click the floating **👩‍⚕️** button to open chat.
2. Ask a specific question (e.g., “mild tension headache remedies?”).
3. If unsure, the assistant will say so and suggest safe next steps.
""")
