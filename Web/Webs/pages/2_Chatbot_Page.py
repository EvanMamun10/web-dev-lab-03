import os

import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.title("Coach Chatbot")
st.write("Ask this sports-focused chatbot about training, strategy, and game preparation.")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "Hi! I am CoachBot. Ask me any sports training question."}
    ]

for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_prompt = st.chat_input("Ask CoachBot something...")

if user_prompt:
    st.session_state.chat_messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.write(user_prompt)

    if not GEMINI_API_KEY.strip():
        error_text = "Missing Gemini API key. Add your key near the top of this file."
        st.session_state.chat_messages.append({"role": "assistant", "content": error_text})
        with st.chat_message("assistant"):
            st.error(error_text)
    else:
        try:
            genai.configure(api_key=GEMINI_API_KEY.strip())
            model = genai.GenerativeModel("gemini-2.5-flash")

            history_text = ""
            for msg in st.session_state.chat_messages[:-1]:
                role_label = "User" if msg["role"] == "user" else "CoachBot"
                history_text += f"{role_label}: {msg['content']}\n"

            full_prompt = (
                "You are CoachBot, a helpful sports assistant. "
                "Keep answers short, practical, and school-appropriate.\n\n"
                f"Conversation so far:\n{history_text}\n"
                f"User: {user_prompt}\nCoachBot:"
            )

            response = model.generate_content(full_prompt)
            bot_reply = response.text.strip() if response and response.text else "I could not generate a reply."

            st.session_state.chat_messages.append({"role": "assistant", "content": bot_reply})
            with st.chat_message("assistant"):
                st.write(bot_reply)

        except Exception as e:
            fallback = f"Gemini error: {type(e).__name__}: {e}"
            st.session_state.chat_messages.append({"role": "assistant", "content": fallback})
            with st.chat_message("assistant"):
                st.error(fallback)
                st.exception(e)
