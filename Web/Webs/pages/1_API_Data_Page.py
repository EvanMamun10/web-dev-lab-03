import requests
import streamlit as st

st.title("Sports Weather Dashboard")
st.write("Use current weather conditions to plan practice or game-day activity.")

# TODO: Paste your OpenWeather API key below.
# Example: OPENWEATHER_API_KEY = "your_api_key_here"
OPENWEATHER_API_KEY = "AIzaSyAgJ_xdTmfqGpv07Kdid1UYgb9oTKo7wnI"

city = st.text_input("Enter a city", value="Atlanta")
unit_choice = st.selectbox("Temperature unit", ["Fahrenheit", "Celsius"])
units_param = "imperial" if unit_choice == "Fahrenheit" else "metric"
temp_unit_label = "F" if units_param == "imperial" else "C"


def get_weather_data(input_city, api_key, units):
    endpoint = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": input_city, "appid": api_key, "units": units}
    response = requests.get(endpoint, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


if st.button("Get Weather"):
    if not OPENWEATHER_API_KEY.strip():
        st.error("Missing API key. Add your OpenWeather API key near the top of this file.")
    elif not city.strip():
        st.error("Please enter a valid city name.")
    else:
        try:
            weather_data = get_weather_data(city.strip(), OPENWEATHER_API_KEY.strip(), units_param)

            weather_main = weather_data["weather"][0]["main"]
            weather_description = weather_data["weather"][0]["description"].title()
            icon_code = weather_data["weather"][0]["icon"]
            temperature = weather_data["main"]["temp"]
            feels_like = weather_data["main"]["feels_like"]
            humidity = weather_data["main"]["humidity"]
            wind_speed = weather_data["wind"]["speed"]

            st.subheader(f"Current Weather in {weather_data['name']}")
            st.write(f"Condition: **{weather_main}** ({weather_description})")
            st.write(f"Temperature: **{temperature}°{temp_unit_label}**")
            st.write(f"Feels Like: **{feels_like}°{temp_unit_label}**")
            st.write(f"Humidity: **{humidity}%**")

            wind_unit = "mph" if units_param == "imperial" else "m/s"
            st.write(f"Wind Speed: **{wind_speed} {wind_unit}**")

            icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
            st.image(icon_url, caption="Live weather icon from OpenWeather")

            chart_data = {
                "Metric": ["Temperature", "Feels Like", "Humidity", "Wind Speed"],
                "Value": [temperature, feels_like, humidity, wind_speed],
            }
            st.bar_chart(chart_data, x="Metric", y="Value")

            st.subheader("Sports Recommendation")
            if weather_main in ["Thunderstorm", "Snow", "Tornado"]:
                st.warning("Indoor training is recommended due to severe weather.")
            elif weather_main in ["Rain", "Drizzle"]:
                st.info("Light outdoor activity is okay, but bring rain gear.")
            elif temperature > 90 and units_param == "imperial":
                st.warning("Very hot conditions. Reduce intensity and hydrate often.")
            elif temperature > 32 and units_param == "metric":
                st.warning("Very hot conditions. Reduce intensity and hydrate often.")
            elif temperature < 45 and units_param == "imperial":
                st.info("Cool weather. Warm up longer before activity.")
            elif temperature < 7 and units_param == "metric":
                st.info("Cool weather. Warm up longer before activity.")
            else:
                st.success("Conditions look good for regular outdoor practice.")

        except requests.exceptions.HTTPError:
            st.error("Could not find weather for that city. Check spelling and try again.")
        except requests.exceptions.RequestException:
            st.error("Network/API error occurred. Please try again in a moment.")
        except (KeyError, TypeError, ValueError):
            st.error("Received unexpected data from API. Please retry.")
