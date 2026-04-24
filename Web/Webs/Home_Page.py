import streamlit as st

# Title of App
st.title("Sports Weather and Coach Chatbot")

# Assignment Data
# TODO: Fill out your team number, section, and team members
st.header("CS 1301")
st.subheader("Web Development - Section X")
st.subheader("Evan Mamun, Linh Truong")


st.write("""
Welcome to our Streamlit app! Use the sidebar to navigate between pages.

1. **Sports Weather Dashboard**: Enter a city and view live weather data for sports planning.
2. **Coach Chatbot**: Ask a general sports-focused AI assistant for training and game-day advice.
3. **Game Day Broadcast Script**: Feeds live weather into Gemini to generate an ESPN-style pre-game segment.
4. **Activity Planner Bot**: A chatbot that uses the weather for your city as context to help plan your day.

This project uses the OpenWeather API for live weather data and the Google Gemini API for AI-generated content.
""")

