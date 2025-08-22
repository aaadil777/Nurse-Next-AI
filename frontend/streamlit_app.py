import os, requests, streamlit as st

st.set_page_config(page_title="AI Nurse (Educational)", layout="centered")
st.title("AI Nurse (Educational)")
st.caption("Not medical advice. For emergencies, call your local emergency number.")

backend_url = os.getenv("BACKEND_URL", "http://localhost:8000/chat")

if "history" not in st.session_state:
    st.session_state.history = [
        {"role": "assistant", "content": "Hi! I can share general health information. What's going on?"}
    ]

# render history
for m in st.session_state.history:
    with st.chat_message(m["role"]):
        st.write(m["content"])

# input
if prompt := st.chat_input("Type your question…"):
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # keep context short for cost and speed
    payload = {"messages": st.session_state.history[-10:]}
    try:
        r = requests.post(backend_url, json=payload, timeout=60)
        r.raise_for_status()
        reply = r.json().get("content", "Sorry—no response.")
    except Exception as e:
        reply = f"Backend error: {e}"

    st.session_state.history.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.write(reply)
