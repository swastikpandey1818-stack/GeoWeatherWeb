from geopy.geocoders import Nominatim
import requests
import streamlit as st

st.title("**Weather App**")
st.write("**Enter a city name to get the current temperature with longitude and latitude and weather conditions.**")
input_city = st.text_input("**Enter a city name to get the current temperature:**")

button = st.button("**Get Weather**")

def get_weather_desc(code):
    """Translates Open-Meteo WMO weather codes into readable descriptions."""
    codes = {
        0: "Clear sky ☀️",
        1: "Mainly clear 🌤️", 2: "Partly cloudy ⛅", 3: "Overcast ☁️",
        45: "Foggy 🌫️", 48: "Depositing rime fog 🌫️",
        51: "Light drizzle 🌧️", 53: "Moderate drizzle 🌧️", 55: "Dense drizzle 🌧️",
        61: "Slight rain 🌧️", 63: "Moderate rain 🌧️", 65: "Heavy rain Status 🌧️",
        71: "Slight snow ❄️", 73: "Moderate snow ❄️", 75: "Heavy snow ❄️",
        80: "Slight rain showers 🌦️", 81: "Moderate rain showers 🌦️", 82: "Violent rain showers ⛈️",
        95: "Thunderstorm 🌩️", 96: "Thunderstorm with slight hail ⛈️", 99: "Thunderstorm with heavy hail ⛈️"
    }
    return codes.get(code, f"Unknown Code ({code})")


def longitude_latitude(city_name):
    geolocator = Nominatim(user_agent="geoapp")
    location = geolocator.geocode(city_name)


    if location:
        latitude = location.latitude
        longitude = location.longitude

        latitude = f"{latitude:.2f}"
        longitude = f"{longitude:.2f}"

        return latitude, longitude
    
    else:


        st.warning("City not found. Please enter a valid city name.")
        return None, None
    


def get_weather(latitude, longitude):
    # Build the API URL with our parameters
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,weathercode,windspeed_10m,relative_humidity_2m&timezone=auto"

    # Make the request
    response = requests.get(url)
    data = response.json()
    
    st.subheader(f"**Weather Information for {input_city}:**")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Temperature (°C)", value=f"{data['current']['temperature_2m']} °C")
        st.metric(label="**wind speed (km/h)**", value=f"{data['current']['windspeed_10m']} km/h")

        
    with col2:
        st.metric(label="**Relative Humidity (%)**", value=f"{data['current']['relative_humidity_2m']} %")
        st.metric(label="**Weather Condition**", value=get_weather_desc(data['current']['weathercode']))
    

    st.write(f"**Coordinates:** Latitude {latitude}, Longitude {longitude}")

if button:
    latitude, longitude = longitude_latitude(input_city)
    if latitude and longitude:
        get_weather(latitude, longitude)
