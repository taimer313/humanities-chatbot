import streamlit as st
import google.generativeai as genai


# ============================
# PAGE SETTINGS
# ============================
st.set_page_config(page_title="Humanities Chatbot", page_icon="🎓")

st.title("🎓 Humanities Chatbot")


# ============================
# API KEY
# ============================
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Missing GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])


# ============================
# SYSTEM INSTRUCTION
# ============================
HUMANITIES_PROMPT = """
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
"""

# ============================
# LOAD MODEL + CHAT SESSION
# ============================
@st.cache_resource
def load_model_and_session():
    try:
        # Use one of the available models from your list
        model_names_to_try = [
            "models/gemini-2.0-flash-001",  # Stable flash model
            "models/gemini-2.0-flash",      # Alternative flash
            "models/gemini-2.5-flash",      # Newer flash model
            "models/gemini-pro-latest",     # Pro model
        ]
        
        model = None
        working_model = None
        
        for model_name in model_names_to_try:
            try:
                model = genai.GenerativeModel(
                    model_name,
                    system_instruction=HUMANITIES_PROMPT
                )
                # Test if model works with a simple message
                test_chat = model.start_chat(history=[])
                test_response = test_chat.send_message("Hello")
                if test_response.text:
                    working_model = model_name
                    st.sidebar.success(f"✅ Using model: {model_name}")
                    break
            except Exception as e:
                st.sidebar.write(f"❌ {model_name} failed: {str(e)[:50]}...")
                continue
                
        if working_model is None:
            st.error("No working model found. Trying gemini-2.0-flash-001 as fallback.")
            model = genai.GenerativeModel(
                "models/gemini-2.0-flash-001",
                system_instruction=HUMANITIES_PROMPT
            )
            working_model = "models/gemini-2.0-flash-001 (fallback)"
            
        return model.start_chat(history=[])
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

chat_session = load_model_and_session()


# ============================
# SESSION STATE
# ============================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ============================
# INPUT BOX WITH FORM
# ============================
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input(
        "Ask something:",
        placeholder="Type here...",
        key="user_input_form"
    )
    submitted = st.form_submit_button("Send")

# ============================
# HANDLE MESSAGE
# ============================
if submitted and user_input.strip():
    user_msg = user_input.strip()

    st.session_state.chat_history.append(("You", user_msg))

    try:
        if chat_session is None:
            st.error("Chat session not initialized. Please refresh the page.")
        else:
            with st.spinner("Thinking..."):
                response = chat_session.send_message(user_msg)
                bot_reply = response.text
            
            st.session_state.chat_history.append(("Bot", bot_reply))
            
    except Exception as e:
        error_msg = f"⚠️ Error: {str(e)}"
        st.session_state.chat_history.append(("Bot", error_msg))
        st.error(f"API Error: {e}")


# ============================
# DISPLAY CHAT
# ============================
for speaker, msg in st.session_state.chat_history:
    if speaker == "You":
        st.markdown(f"**🧑 You:** {msg}")
    else:
        st.markdown(f"**🤖 Bot:** {msg}")

# Add a clear button
if st.button("Clear Chat"):
    st.session_state.chat_history = []
    st.rerun()

# Display available models in sidebar for debugging
st.sidebar.subheader("Debug Info")
if st.sidebar.button("Refresh App"):
    st.rerun()
