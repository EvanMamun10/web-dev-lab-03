import os

import requests
import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.title("Game Day Broadcast Script")
st.write("Pull today's weather and turn it into an ESPN-style pre-game segment with Gemini.")

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

input_col, setting_col = st.columns(2)

with input_col:
    city = st.text_input("City", value="Atlanta")
    sport = st.selectbox(
        "Sport",
        ["Football", "Baseball", "Soccer", "Track and Field", "Tennis", "Golf"],
    )

with setting_col:
    team_name = st.text_input("Home team name", value="Yellow Jackets")
    tone = st.select_slider(
        "Broadcaster tone",
        options=["Calm", "Standard", "Hyped"],
        value="Standard",
    )

script_length = st.slider("Script length (sentences)", 3, 10, 6)


def get_weather(input_city, api_key):
    endpoint = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": input_city, "appid": api_key, "units": "imperial"}
    response = requests.get(endpoint, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


if st.button("Generate Broadcast Script"):
    if not city.strip():
        st.error("Please enter a city.")
    elif not team_name.strip():
        st.error("Please enter a home team name.")
    else:
        try:
            data = get_weather(city.strip(), OPENWEATHER_API_KEY)

            conditions = data["weather"][0]["description"].title()
            temp = data["main"]["temp"]
            feels = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            wind = data["wind"]["speed"]
            location = data["name"]

            with st.container(border=True):
                st.subheader(f"Live Conditions in {location}")
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Temp", f"{temp}°F")
                m2.metric("Feels Like", f"{feels}°F")
                m3.metric("Humidity", f"{humidity}%")
                m4.metric("Wind", f"{wind} mph")
                st.caption(f"Sky: {conditions}")

            prompt = (
                f"You are a professional ESPN-style sports broadcaster. "
                f"Write a {tone.lower()} pre-game weather and field-conditions segment "
                f"for a {sport} game in {location} where the home {team_name} are hosting a rival. "
                f"Keep it to about {script_length} sentences, make it sound spoken on air, "
                f"and work these real conditions in naturally: "
                f"{conditions}, {temp} degrees Fahrenheit (feels like {feels}), "
                f"humidity {humidity} percent, wind {wind} mph. "
                f"Explain how these conditions affect play style and player comfort in {sport}. "
                f"Do not include stage directions in brackets."
            )

            genai.configure( api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt)
            script = response.text.strip() if response and response.text else ""

            script_tab, prompt_tab = st.tabs(["On-Air Script", "Prompt Sent to Gemini"])

            with script_tab:

                if not script:
                    st.warning(" Gemini returned an empty response. Try again.")
                else:
                    with st.container(border=True):
                        st.write(script)

            with prompt_tab:

                st.code(prompt, language="text")

        except requests.exceptions.HTTPError as e:
            st.error(f"Weather API HTTP error: {e}")
        except requests.exceptions.RequestException as e:
            st.error(f"Network error talking to weather API: {e}")
        except (KeyError, TypeError, ValueError) as e:
            st.error(f"Unexpected weather API response: {e}")
        except Exception as e:
            st.error(f"Gemini error: {type(e).__name__}: {e}")
            st.exception(e)
