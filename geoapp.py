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

# 🔑 Your active OpenWeatherMap API key injected safely
API_KEY = "187020f5dd44511bea738e0bac59896d"

st.title("**Geo Weather App-Py**")
st.write("**Enter a city name to get the current temperature with longitude and latitude and weather conditions.**")

input_city = st.text_input("**Enter a city name to get the current temperature:**")
button = st.button("**Get Weather**")


@st.cache_data(ttl=3600)
def longitude_latitude(city_name):
    """Safely geocodes a location name to dynamic coordinates with integrated caching."""
    geolocator = Nominatim(user_agent="geoapp_swastik_weather")
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


def get_weather_data(lat, lon):
    """Fetches real-time current weather data using the Standard Free API endpoint."""
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            st.error(f"❌ Current Weather API Error: {response.json().get('message', 'Unknown Error')}")
            st.stop()
        return response.json()
    except Exception:
        st.error("⚡ Unable to connect to OpenWeatherMap.")
        st.stop()


def get_forecast_data(lat, lon):
    """Fetches 5-day / 3-hour forecast data using the Standard Free API endpoint."""
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            st.error(f"❌ Forecast API Error: {response.json().get('message', 'Unknown Error')}")
            st.stop()
        return response.json()
    except Exception:
        st.error("⚡ Unable to fetch forecast array elements.")
        st.stop()


def render_weather_dashboard(current_data, forecast_data, lat, lon):
    """Paints all processed weather variables and UI frameworks onto the webpage."""
    
    # --- 1. CURRENT WEATHER SECTION ---
    weather_info = current_data['weather'][0]
    temp = current_data['main']['temp']
    wind_speed = current_data['wind']['speed'] * 3.6  # Convert m/s to km/h
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
        st.markdown(
            f"**Weather Condition:** {condition_desc} <img src='{icon_url}' width='45' style='vertical-align:middle;'>", 
            unsafe_allow_html=True
        )
    
    st.write(f"**Coordinates:** Latitude {lat:.2f}, Longitude {lon:.2f}")
    st.write("**This Website is Made by Swatik Pandey**")
    
    # --- 2. 5-DAY FORECAST PROCESSING ENGINE ---
    st.markdown("### 📅 **5-Day Forecast**")
    
    # OpenWeatherMap provides data every 3 hours. We pick one mid-day snapshot (e.g., 12:00 PM) for each day.
    forecast_list = forecast_data['list']
    daily_snapshots = []
    seen_dates = set()
    
    for item in forecast_list:
        dt_obj = datetime.datetime.fromtimestamp(item['dt'])
        date_str = dt_obj.strftime("%Y-%m-%d")
        
        # Grab a snapshot once per unique calendar day
        if date_str not in seen_dates:
            # We skip today's date if it's already running in the "Current Weather" box above
            if date_str != datetime.datetime.now().strftime("%Y-%m-%d"):
                daily_snapshots.append(item)
                seen_dates.add(date_str)
        
        # Limit to 5 clean forecast columns max
        if len(daily_snapshots) == 5:
            break

    # Render columns responsively
    forecast_cols = st.columns(5)
    for i, day in enumerate(daily_snapshots):
        with forecast_cols[i]:
            date_obj = datetime.datetime.fromtimestamp(day['dt'])
            day_name = date_obj.strftime("%a")
            day_date = date_obj.strftime("%b %d")
            
            day_icon = day['weather'][0]['icon']
            day_icon_url = f"http://openweathermap.org/img/wn/{day_icon}.png"
            
            # The 5-day tier provides the expected atmospheric temperatures cleanly
            max_temp = day['main']['temp_max']
            min_temp = day['main']['temp_min']
            
            st.markdown(f"**{day_name}**")
            st.caption(day_date)
            st.markdown(f"<img src='{day_icon_url}' width='45'>", unsafe_allow_html=True)
            st.markdown(f"🔥**{int(max_temp)}°**")
            st.markdown(f"❄️**{int(min_temp)}°**")
            
    # --- 3. GOOGLE MAPS SATELLITE EMBED ---
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
        lat, lon = longitude_latitude(input_city)
        if lat is not None and lon is not None:
            # Dual fetch strategy bypassing any credit card requirement limitations
            current_payload = get_weather_data(lat, lon)
            forecast_payload = get_forecast_data(lat, lon)
            
            render_weather_dashboard(current_payload, forecast_payload, lat, lon)