# Streamlit code
# app.py
import os
import streamlit as st
import google.generativeai as genai

# Try Streamlit secrets first (works on Streamlit Cloud), else environment variable.
API_KEY = None
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    st.error(
        "No API key found. Set GEMINI_API_KEY in Streamlit secrets (if deploying) "
        "or in your environment variables (for local run)."
    )
    st.stop()

genai.configure(api_key=API_KEY)

SYSTEM_PROMPT = """
You are an AI Humanities Chatbot.

Identity:
- You respond through philosophy, psychology, ethics, culture, literature, and history.
- You provide deeper meaning and reflective insights.

Response structure:
1. Surface answer
2. Humanities interpretation
3. A reflective question

Tone:
Warm, thoughtful, curious, grounded.

IMPORTANT RULES:
- Never output anything in JSON, XML, code blocks, or structured data.
- Never output or mention roles like "user", "model", "assistant", or "system".
- Never include metadata or internal formatting.
- Always answer identity questions in plain text.
- If asked "Who are you?" reply naturally:
  "I am a Humanities-focused AI designed to interpret questions through perspectives from philosophy, culture, psychology, ethics, and history."
"""

st.set_page_config(page_title="Humanities Chatbot", layout="centered")
st.title("Humanities Chatbot (Gemini)")

# Initialize session state messages list
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "bot", "content": "Hello — ask me anything about culture, ethics, literature, or history."}
    ]

# show conversation
for i, msg in enumerate(st.session_state["messages"]):
    role = msg.get("role")
    content = msg.get("content")
    if role == "user":
        st.markdown(f"**You:** {content}")
    elif role == "bot":
        st.markdown(f"**Bot:** {content}")

# input area
user_input = st.text_input("Your message", key="user_input")

col1, col2 = st.columns([1, 4])
with col1:
    send = st.button("Send")
with col2:
    clear = st.button("Clear conversation")

if clear:
    st.session_state["messages"] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "bot", "content": "Hello — ask me anything about culture, ethics, literature, or history."}
    ]
    st.experimental_rerun()

if send and user_input:
    # append user message
    st.session_state["messages"].append({"role": "user", "content": user_input})
    # call Gemini chat API
    try:
        model = genai.GenerativeModel(
            "gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT
        )
        session = model.start_chat()
        response = session.send_message(user_input)
        bot_text = response.text

    except Exception as e:
        bot_text = f"Error calling API: {e}"

    st.session_state["messages"].append({"role": "bot", "content": bot_text})
    # clear input
    st.session_state["user_input"] = ""
    st.experimental_rerun()
