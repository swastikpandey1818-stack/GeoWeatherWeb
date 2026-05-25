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

# 🔑 OpenWeatherMap API Key Configuration
API_KEY = "187020f5dd44511bea738e0bac59896d"

st.title("**Geo Weather App-Py**")
st.write("**Enter a city name to get the current temperature with longitude and latitude and weather conditions.**")

input_city = st.text_input("**Enter a city name to get the current temperature:**")
button = st.button("**Get Weather**")


@st.cache_data(ttl=3600)
def longitude_latitude(city_name):
    """Safely geocodes a location name to dynamic coordinates with integrated caching."""
    geolocator = Nominatim(user_agent="geoapp_swastik_hybrid_engine")
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


def get_weather_desc_meteo(code, is_day=1):
    """Fallback translator for Open-Meteo WMO weather codes."""
    codes = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Foggy", 48: "Depositing rime fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
        80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
        95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
    }
    desc = codes.get(code, f"Unknown Code ({code})")
    if is_day == 0:
        if code == 0: return "Clear Night 🌙"
        if code == 1: return "Mainly Clear Night 🌌"
        return f"{desc} ☁️"
    else:
        if code == 0: return "Clear sky ☀️"
        if code == 1: return "Mainly clear 🌤️"
        if code == 2: return "Partly cloudy ⛅"
        return f"{desc} ☀️"


def get_forecast_emoji_meteo(code):
    """Fallback emoji dictionary mapping for Open-Meteo forecast symbols."""
    emoji_map = {
        0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
        45: "🌫️", 48: "🌫️", 51: "🌧️", 53: "🌧️", 55: "🌧️",
        61: "🌧️", 63: "🌧️", 65: "🌧️", 71: "❄️", 73: "❄️", 75: "❄️",
        80: "🌦️", 81: "🌦️", 82: "⛈️", 95: "🌩️", 96: "⛈️", 99: "⛈️"
    }
    return emoji_map.get(code, "🌡️")


def fetch_weather_pipeline(lat, lon):
    """Dual-engine core logic wrapper using a try-except strategy to fetch weather data."""
    try:
        # 🌟 Engine A: Attempt to fetch from OpenWeatherMap (Primary)
        current_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={API_KEY}"
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={API_KEY}"
        
        current_res = requests.get(current_url)
        forecast_res = requests.get(forecast_url)
        
        # If the key returns a 401 Unauthorized status code, deliberately trigger the except clause
        if current_res.status_code == 401 or forecast_res.status_code == 401:
            raise ValueError("OpenWeather Key Not Activated")
            
        if current_res.status_code == 200 and forecast_res.status_code == 200:
            return "openweather", current_res.json(), forecast_res.json()
            
    except Exception:
        pass  # Silently ignore the OpenWeather error and execute fallback below
        
    # 🔄 Engine B: Backup Fallback to Open-Meteo API
    meteo_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,weathercode,windspeed_10m,relative_humidity_2m,is_day&daily=weathercode,temperature_2m_max,temperature_2m_min&timezone=auto"
    try:
        meteo_res = requests.get(meteo_url)
        if meteo_res.status_code == 200:
            return "openmeteo", meteo_res.json(), None
    except Exception:
        st.error("🚨 Both weather network engines are currently unreachable. Please try again.")
        st.stop()


def render_dashboard(engine_type, current_data, forecast_data, lat, lon):
    """Dynamically parses and structuralizes layouts depending on which data engine fired."""
    
    if engine_type == "openweather":
        st.info("📊 Powered by OpenWeatherMap Engine")
        
        # OpenWeather Data Parsing
        weather_info = current_data['weather'][0]
        temp = current_data['main']['temp']
        wind_speed = current_data['wind']['speed'] * 3.6
        humidity = current_data['main']['humidity']
        condition_desc = weather_info['description'].title()
        icon_id = weather_info['icon']
        
        st.subheader(f"**Weather Information for {input_city.title()}:**")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Temperature (°C)", value=f"{temp:.1f} °C")
            st.metric(label="Wind Speed (km/h)", value=f"{wind_speed:.1f} km/h")
        with col2:
            st.metric(label="Relative Humidity (%)", value=f"{humidity} %")
            icon_url = f"http://openweathermap.org/img/wn/{icon_id}@2x.png"
            st.markdown(f"**Weather Condition:** {condition_desc} <img src='{icon_url}' width='45' style='vertical-align:middle;'>", unsafe_allow_html=True)
            
        # 5-Day Forecast Build
        st.markdown("### 📅 **5-Day Forecast**")
        forecast_list = forecast_data['list']
        daily_snapshots = []
        seen_dates = set()
        current_date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        
        for item in forecast_list:
            date_str = datetime.datetime.fromtimestamp(item['dt']).strftime("%Y-%m-%d")
            if date_str not in seen_dates and date_str != current_date_str:
                daily_snapshots.append(item)
                seen_dates.add(date_str)
            if len(daily_snapshots) == 5: break
                
        cols = st.columns(5)
        for i, day in enumerate(daily_snapshots):
            with cols[i]:
                date_obj = datetime.datetime.fromtimestamp(day['dt'])
                st.markdown(f"**{date_obj.strftime('%a')}**")
                st.caption(date_obj.strftime("%b %d"))
                st.markdown(f"<img src='http://openweathermap.org/img/wn/{day['weather'][0]['icon']}.png' width='45'>", unsafe_allow_html=True)
                st.markdown(f"🔥**{int(day['main']['temp_max'])}°**")
                st.markdown(f"❄️**{int(day['main']['temp_min'])}°**")

    else:
        st.info("🔄 OpenWeather key pending activation. Auto-switched to backup Open-Meteo Engine.")
        
        # Open-Meteo Fallback Data Parsing
        current_data_meteo = current_data['current']
        is_day = current_data_meteo.get('is_day', 1)
        
        st.subheader(f"**Weather Information for {input_city.title()}:**")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Temperature (°C)", value=f"{current_data_meteo['temperature_2m']} °C")
            st.metric(label="Wind Speed (km/h)", value=f"{current_data_meteo['windspeed_10m']} km/h")
        with col2:
            st.metric(label="Relative Humidity (%)", value=f"{current_data_meteo['relative_humidity_2m']} %")
            st.metric(label="Weather Condition", value=get_weather_desc_meteo(current_data_meteo['weathercode'], is_day))
            
        # 7-Day Forecast Fallback Build
        st.markdown("### 📅 **7-Day Forecast**")
        daily_data = current_data['daily']
        dates = daily_data['time']
        max_temps = daily_data['temperature_2m_max']
        min_temps = daily_data['temperature_2m_min']
        weather_codes = daily_data['weathercode']
        
        cols = st.columns(7)
        for i in range(7):
            with cols[i]:
                date_obj = datetime.datetime.strptime(dates[i], "%Y-%m-%d")
                st.markdown(f"**{date_obj.strftime('%a')}**")
                st.caption(date_obj.strftime("%b %d"))
                st.markdown(f"### {get_forecast_emoji_meteo(weather_codes[i])}")
                st.markdown(f"🔥**{int(max_temps[i])}°**")
                st.markdown(f"❄️**{int(min_temps[i])}°**")

    # --- 3. UNIVERSAL SATELLITE VIEW ---
    st.markdown("### 🛰️ **Satellite View**")
    google_maps_url = f"https://maps.google.com/maps?q={lat},{lon}&t=k&z=14&output=embed"
    components.html(
        f'<iframe src="{google_maps_url}" width="100%" height="400" style="border:0; border-radius:10px;" allowfullscreen="" loading="lazy"></iframe>',
        height=410
    )


# --- 4. EXECUTION GATEWAY ---
if button:
    if not input_city.strip():
        st.error("Please enter a city name first!")
    else:
        latitude, longitude = longitude_latitude(input_city)
        if latitude is not None and longitude is not None:
            engine, dataset1, dataset2 = fetch_weather_pipeline(latitude, longitude)
            render_dashboard(engine, dataset1, dataset2, latitude, longitude)