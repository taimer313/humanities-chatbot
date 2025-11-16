import streamlit as st
import google.generativeai as genai


# ============================
# 1. CONFIGURE PAGE
# ============================
st.set_page_config(
    page_title="Humanities Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.title("🎓 Humanities Chatbot")


# ============================
# 2. LOAD API KEY SAFELY
# ============================
# MUST be set in Streamlit Secrets as GEMINI_API_KEY
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Missing GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])


# ============================
# 3. LOAD MODEL SAFELY (cached)
# ============================
@st.cache_resource
def load_model():
    return genai.GenerativeModel("gemini-1.5-flash")

model = load_model()


# ============================
# 4. INITIALIZE SESSION STATE
# ============================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "user_input" not in st.session_state:
    st.session_state.user_input = ""


# ============================
# 5. RESET INPUT FIELD CALLBACK
# ============================
def reset_input():
    st.session_state.user_input = ""


# ============================
# 6. CHAT INPUT BOX
# ============================
st.text_input(
    "Ask something:",
    key="user_input",
    on_change=reset_input,
    placeholder="Type your question here...",
)


# ============================
# 7. ON SEND → GENERATE RESPONSE
# ============================
if st.session_state.user_input.strip():
    user_msg = st.session_state.user_input.strip()

    # Add to chat history
    st.session_state.chat_history.append(("You", user_msg))

    try:
        response = model.generate_content(user_msg)
        bot_reply = response.text
    except Exception as e:
        bot_reply = f"⚠️ Something went wrong: {str(e)}"

    # Save bot response
    st.session_state.chat_history.append(("Bot", bot_reply))


# ============================
# 8. DISPLAY CHAT HISTORY
# ============================
for speaker, msg in st.session_state.chat_history:
    if speaker == "You":
        st.markdown(f"**🧑 You:** {msg}")
    else:
        st.markdown(f"**🤖 Bot:** {msg}")
