import datetime
import requests
import streamlit as st
import streamlit.components.v1 as components
from geopy.geocoders import Nominatim

# 1. Page Configuration Setup
st.set_page_config(
    page_title="Swastik GeoWeather - Live Weather App",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("**Geo Weather App-Py**")
st.write("**Enter a city name to get the current temperature with longitude and latitude and weather conditions.**")

input_city = st.text_input("**Enter a city name to get the current temperature:**")
button = st.button("**Get Weather**")


def get_weather_desc(code, is_day=1):
    """Translates Open-Meteo WMO weather codes into readable descriptions with day/night awareness."""
    # Base description dictionary
    codes = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Foggy", 48: "Depositing rime fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain Status",
        71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
        80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
        95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
    }
    
    desc = codes.get(code, f"Unknown Code ({code})")
    
    # Contextual Day/Night Emojis
    if is_day == 0:  # It's nighttime!
        if code == 0: return "Clear Night 🌙"
        if code == 1: return "Mainly Clear Night 🌌"
        if code in [2, 3]: return f"{desc} ☁️"
        if code in [45, 48]: return f"{desc} 🌫 `"
        if code in [51, 53, 55, 61, 63, 65, 80, 81]: return f"{desc} 🌧 ️"
        return f"{desc} ⏰"
    else:  # It's daytime!
        if code == 0: return "Clear sky ☀️"
        if code == 1: return "Mainly clear 🌤️"
        if code == 2: return "Partly cloudy ⛅"
        if code == 3: return "Overcast ☁️"
        if code in [45, 48]: return f"{desc} 🌫 ️"
        if code in [51, 53, 55, 61, 63, 65, 80, 81]: return f"{desc} 🌧 ️"
        return f"{desc} ☀️"


@st.cache_data(ttl=3600)
def longitude_latitude(city_name):
    """Safely geocodes a location name to dynamic coordinates with integrated caching."""
    geolocator = Nominatim(user_agent="geoapp")
    try:
        location = geolocator.geocode(city_name)
        if location:
            return location.latitude, location.longitude
        else:
            st.error("🔍 City not found. Please enter a valid city name.")
            st.stop()
    except Exception:
        st.error("🌐 Geocoding service is temporarily busy. Please try again in a moment.")
        st.stop()


def get_weather(latitude, longitude):
    """Queries the weather payload engine and paints all elements to the web page UI."""
    # Unified API call requesting current parameters, is_day tracker, and 7-day daily arrays
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,weathercode,windspeed_10m,relative_humidity_2m,is_day&daily=weathercode,temperature_2m_max,temperature_2m_min&timezone=auto"

    response = requests.get(url)
    data = response.json()
    
    current_data = data['current']
    is_day = current_data.get('is_day', 1)  # Reads 1 for daytime, 0 for nighttime
    
    # 1. Display Current Weather Metrics
    st.subheader(f"**Weather Information for {input_city.title()}:**")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Temperature (°C)", value=f"{current_data['temperature_2m']} °C")
        st.metric(label="Wind Speed (km/h)", value=f"{current_data['windspeed_10m']} km/h")
        
    with col2:
        st.metric(label="Relative Humidity (%)", value=f"{current_data['relative_humidity_2m']} %")
        st.metric(label="Weather Condition", value=get_weather_desc(current_data['weathercode'], is_day))
    
    st.write(f"**Coordinates:** Latitude {latitude:.2f}, Longitude {longitude:.2f}")
    st.write("**This Website is Made by Swatik Pandey**")
    
    # 2. Display 7-Day Forecast Grid
    st.markdown("### 📅 **7-Day Forecast**")
    daily_data = data['daily']
    dates = daily_data['time']
    max_temps = daily_data['temperature_2m_max']
    min_temps = daily_data['temperature_2m_min']
    weather_codes = daily_data['weathercode']
    
    forecast_cols = st.columns(7)
    for i in range(7):
        with forecast_cols[i]:
            date_obj = datetime.datetime.strptime(dates[i], "%Y-%m-%d")
            day_name = date_obj.strftime("%a")
            day_date = date_obj.strftime("%b %d")
            
            # Use daytime defaults (is_day=1) for general future forecast icons
            condition_desc = get_weather_desc(weather_codes[i], is_day=1)
            emoji = condition_desc.split()[-1] if len(condition_desc.split()) > 0 else "🌡️"
            
            st.markdown(f"**{day_name}**")
            st.caption(day_date)
            st.markdown(f"### {emoji}")
            st.markdown(f"🔥**{int(max_temps[i])}°**")
            st.markdown(f"❄️**{int(min_temps[i])}°**")
            
    # 3. Display Secure Universal Google Maps Satellite Embed
    st.markdown("### 🛰️ **Satellite View**")
    google_maps_url = f"https://maps.google.com/maps?q={latitude},{longitude}&t=k&z=14&output=embed"
    
    components.html(
        f'<iframe src="{google_maps_url}" width="100%" height="400" style="border:0; border-radius:10px;" allowfullscreen="" loading="lazy"></iframe>',
        height=410
    )


# --- 4. EXECUTION GATEWAY ---
if button:
    if not input_city.strip():
        st.error("Please enter a city name first!")
    else:
        lat, lon = longitude_latitude(input_city)
        if lat is not None and lon is not None:
            get_weather(lat, lon)