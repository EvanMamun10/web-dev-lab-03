import os

import requests
import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.title("Activity Planner Bot")
st.write("Load your city's weather, then chat about whether today is good for your plans.")

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


def get_weather(input_city, api_key):
    endpoint = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": input_city, "appid": api_key, "units": "imperial"}
    response = requests.get(endpoint, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


with st.sidebar:
    st.header("Planner Setup")
    city = st.text_input("Your city", value="Atlanta")
    default_activity = st.selectbox(
        "Default activity",
        ["Light walk", "Run", "Team practice", "Outdoor game", "Hike", "Bike ride"],
    )

    load_clicked = st.button("Load / Reset Weather")

    if load_clicked:
        if not city.strip():
            st.error("Please enter a city.")
        else:
            try:
                data = get_weather(city.strip(), OPENWEATHER_API_KEY)
                st.session_state.planner_weather = {
                    "city": data["name"],
                    "conditions": data["weather"][0]["description"].title(),
                    "temp": data["main"]["temp"],
                    "feels": data["main"]["feels_like"],
                    "humidity": data["main"]["humidity"],
                    "wind": data["wind"]["speed"],
                }
                st.session_state.planner_activity = default_activity
                st.session_state.planner_messages = [
                    {
                        "role": "assistant",
                        "content": (
                            f"Got it. I've pulled the current weather for {data['name']}. "
                            f"Ask me if today is good for a {default_activity.lower()}, or anything else."
                        ),
                    }
                ]
                st.success("Weather loaded.")
            except requests.exceptions.HTTPError:
                st.error("Could not find that city.")
            except requests.exceptions.RequestException:
                st.error("Network error. Try again.")
            except (KeyError, TypeError, ValueError):
                st.error("Unexpected API response.")


if "planner_weather" not in st.session_state:
    st.info("Use the sidebar to load weather for a city before chatting.")
    st.stop()

weather = st.session_state.planner_weather
activity = st.session_state.planner_activity

with st.container(border=True):
    st.subheader(f"Weather context: {weather['city']}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Temp", f"{weather['temp']}°F")
    c2.metric("Feels", f"{weather['feels']}°F")
    c3.metric("Humidity", f"{weather['humidity']}%")
    c4.metric("Wind", f"{weather['wind']} mph")
    st.caption(f"Conditions: {weather['conditions']}  |  Default activity: {activity}")

if "planner_messages" not in st.session_state:
    st.session_state.planner_messages = []

for message in st.session_state.planner_messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_prompt = st.chat_input("Ask about your plans...")

if user_prompt:
    st.session_state.planner_messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.write(user_prompt)

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")

        weather_context = (
            f"Current weather in {weather['city']}: {weather['conditions']}, "
            f"{weather['temp']}F (feels like {weather['feels']}F), "
            f"humidity {weather['humidity']}%, wind {weather['wind']} mph. "
            f"User's default activity: {activity}."
        )

        history_text = ""
        for msg in st.session_state.planner_messages[:-1]:
            role_label = "User" if msg["role"] == "user" else "Bot"
            history_text += f"{role_label}: {msg['content']}\n"

        full_prompt = (
            "You are ActivityBot, a concise and friendly planner that advises whether "
            "outdoor or indoor plans make sense given real weather conditions. "
            "Reference the actual numbers when relevant, suggest adjustments (hydration, "
            "layers, timing), and keep replies short and school-appropriate.\n\n"
            f"Weather context:\n{weather_context}\n\n"
            f"Conversation so far:\n{history_text}\n"
            f"User: {user_prompt}\nBot:"
        )

        response = model.generate_content(full_prompt)
        bot_reply = response.text.strip() if response and response.text else "I could not generate a reply. Try again."

        st.session_state.planner_messages.append({"role": "assistant", "content": bot_reply})
        with st.chat_message("assistant"):
            st.write(bot_reply)

    except Exception as e:
        fallback = f"Gemini error: {type(e).__name__}: {e}"
        st.session_state.planner_messages.append({"role": "assistant", "content": fallback})
        with st.chat_message("assistant"):
            st.error(fallback)
            st.exception(e)
