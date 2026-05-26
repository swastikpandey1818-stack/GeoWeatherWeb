import streamlit as st
import google.generativeai as genai
import openai
import requests
import pandas as pd
import time
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
# Initialize geolocator
geolocator = Nominatim(user_agent="geoweather_app")
def render_custom_bar_chart():
    categories = ['Coffee', 'Tea', 'Juice', 'Soft Drink', 'Plant-based']
    values = [100, 60, 70, 30, 40]
    
    fig = go.Figure(data=[go.Bar(
        x=categories, y=values,
        marker_color='#E4B062', # Match your specific orange tone
        marker_line_width=0,
        width=0.6
    )])
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False, showticklabels=False),
        margin=dict(l=0, r=0, t=0, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

# Page Configuration
st.set_page_config(page_title="Swastik's GeoWeather Pro", page_icon="🌤️", layout="wide")

# ==========================================
# 💎 PREMIUM GLOBAL CSS CUSTOMIZATIONS
# ==========================================
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Inter', sans-serif;
            background-color: #0E1117;
            color: #E0E0E0;
        }
        
        [data-testid="stHeader"] {
            background: rgba(0,0,0,0);
        }
        
        /* Premium Card Containers */
        .weather-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(4px);
        }
        
        .gradient-text {
            background: min-content;
            background-image: linear-gradient(45deg, #FFD700, #FFA500);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
        }

        div[data-baseweb="input"] {
            background-color: rgba(255, 255, 255, 0.05) !important;
            border-radius: 10px !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }
        
        div.stButton > button {
            background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%) !important;
            color: #000000 !important;
            font-weight: 600 !important;
            border-radius: 10px !important;
            border: none !important;
            padding: 12px 28px !important;
            width: 100%;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(255, 215, 0, 0.2) !important;
        }
        
        div.stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4) !important;
        }
    </style>
""", unsafe_allow_html=True)

def request_with_retry(url, timeout=15, retries=4, backoff=1):
    last_exception = None
    retry_statuses = {429, 500, 502, 503, 504}

    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code in retry_statuses:
                if attempt == retries - 1:
                    response.raise_for_status()
                time.sleep(backoff * (2 ** attempt))
                continue
            response.raise_for_status()
            return response
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as exc:
            last_exception = exc
            if attempt == retries - 1:
                raise
            time.sleep(backoff * (2 ** attempt))
        except requests.exceptions.HTTPError as exc:
            if response is not None and response.status_code in retry_statuses and attempt < retries - 1:
                time.sleep(backoff * (2 ** attempt))
                continue
            raise
    raise last_exception or requests.exceptions.RequestException("Request failed after retries")

@st.cache_data(ttl=600)
def cached_geo_search(city_name_query):
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name_query}&count=5&language=en&format=json"
    response = request_with_retry(geo_url)
    return response.json()

@st.cache_data(ttl=600)
def cached_weather_fetch(lat, lon):
    weather_url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}"
        f"&longitude={lon}&current_weather=true"
        f"&hourly=temperature_2m,relative_humidity_2m"
        f"&daily=weathercode,temperature_2m_max,temperature_2m_min"
        f"&timezone=auto&forecast_days=7"
    )
    response = request_with_retry(weather_url)
    return response.json()

# Helper function to fetch data and store it cleanly in state memory
def fetch_weather_data(city_name_query):
    st.session_state.fetch_error = None
    st.session_state.fetch_error = None
    try:
        # Using geopy instead of Open-Meteo geocoding
        location = geolocator.geocode(city_name_query)
        if location:
            st.session_state.lat = location.latitude
            st.session_state.lon = location.longitude
            st.session_state.display_city = location.address
        else:
            st.session_state.fetch_error = "City not found via GeoPy."
            return
    except Exception as e:
        st.session_state.fetch_error = f"Geocoding error: {e}"
        return
    except requests.exceptions.HTTPError as exc:
        if "429" in str(exc):
            st.session_state.fetch_error = (
                "Too many requests to Open-Meteo. Please wait a minute and try again."
            )
        else:
            st.session_state.fetch_error = f"Geocoding failed: {exc}"
        return
    except Exception as exc:
        st.session_state.fetch_error = f"Geocoding failed: {exc}"
        return

    try:
        res_data = cached_weather_fetch(st.session_state.lat, st.session_state.lon)
        st.session_state.w_data = res_data

        if "current_weather" in res_data:
            st.session_state.temp_val = f"{res_data['current_weather']['temperature']}°C"
            st.session_state.wind_val = f"{res_data['current_weather']['windspeed']} km/h"
            if "hourly" in res_data and "relative_humidity_2m" in res_data["hourly"]:
                st.session_state.hum_val = f"{res_data['hourly']['relative_humidity_2m'][0]}%"
        else:
            st.session_state.fetch_error = "Weather data is unavailable for this location."
    except requests.exceptions.HTTPError as exc:
        if "429" in str(exc):
            st.session_state.fetch_error = (
                "Too many requests to Open-Meteo. Please wait a minute and try again."
            )
        else:
            st.session_state.fetch_error = f"Weather fetch failed: {exc}"
    except Exception as exc:
        st.session_state.fetch_error = f"Weather fetch failed: {exc}"

# Bootstrapping: If the app just opened up, run an initial background fetch for Gorakhpur right away
if st.session_state.w_data is None:
    fetch_weather_data("Gorakhpur")

# Create the 3-Tab navigation layout
tab1, tab2, tab3 = st.tabs(["📊 Live Weather Metrics", "🔮 7-Day Extended Forecast", "💬 Ask GeoWeather AI"])

# ==========================================
# 📊 TAB 1: LIVE WEATHER METRICS & SEARCH
# ==========================================
with tab1:
    st.markdown("""
        <div style='text-align: center; padding: 15px 0px;'>
            <h1 style='font-size: 2.5rem; margin-bottom: 0;'>🚀 <span class='gradient-text'>GeoWeather Pro</span></h1>
            <p style='color: #888888; font-size: 1rem;'>Enterprise-Grade Atmospheric Tracking Engine</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="weather-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0; font-size:1.2rem; color:#FFD700;'>🔍 Search Regional Conditions</h3>", unsafe_allow_html=True)
    city_input = st.text_input("Enter city name:",value = None, placeholder="e.g., Gorakhpur, Delhi, London", label_visibility="collapsed")
    search_button = st.button("Get Live Metrics")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if 'selected_city' not in st.session_state:
     st.session_state.selected_city = None
    if search_button and city_input:
        st.session_state.current_city = city_input
        fetch_weather_data(city_input)

    st.markdown(f"### 📍 Current Analysis for **{st.session_state.display_city}**")
    m_col1, m_col2, m_col3 = st.columns(3)
    
    with m_col1:
        st.markdown(f'<div class="weather-card" style="text-align: center;"><h2>🌡️</h2><p style="color:#888;">Temperature</p><h2>{st.session_state.temp_val}</h2></div>', unsafe_allow_html=True)
    with m_col2:
        st.markdown(f'<div class="weather-card" style="text-align: center;"><h2>💧</h2><p style="color:#888;">Humidity</p><h2>{st.session_state.hum_val}</h2></div>', unsafe_allow_html=True)
    with m_col3:
        st.markdown(f'<div class="weather-card" style="text-align: center;"><h2>💨</h2><p style="color:#888;">Wind Velocity</p><h2>{st.session_state.wind_val}</h2></div>', unsafe_allow_html=True)

    st.markdown('### 🗺️ Geospatial Vector View')
    st.map(pd.DataFrame({'lat': [st.session_state.lat], 'lon': [st.session_state.lon]}), zoom=10)
# ==========================================
# 🔮 TAB 2: PREMIUM FORECAST & INFOGRAPHICS
# ==========================================

def render_forecast_display():
    """Renders the creative cards and table if data exists."""
    if st.session_state.w_data is None or "daily" not in st.session_state.w_data:
        st.warning("Forecast data is currently unavailable. Please try searching for the city again.")
        return

    daily = st.session_state.w_data["daily"]
    if not daily.get("time") or not daily.get("temperature_2m_max"):
        st.warning("Incomplete forecast data received from the API.")
        return

    dates = pd.to_datetime(daily["time"])
    st.subheader(f"Analysis for: **{st.session_state.display_city}**")

    cols = st.columns(7)
    for i, col in enumerate(cols):
        if i < len(daily["weathercode"]):
            code = daily["weathercode"][i]
            emoji = "☀️" if code in [0, 1] else "☁️" if code in [2, 3] else "🌧️"
            with col:
                st.markdown(f"""
                    <div style="padding:10px; text-align:center; background:rgba(255,255,255,0.05); border-radius:10px;">
                        <small>{dates[i].strftime('%a')}</small><br>
                        <span style="font-size:1.5rem;">{emoji}</span><br>
                        <strong>{daily['temperature_2m_max'][i]}°</strong>
                    </div>
                """, unsafe_allow_html=True)

    df = pd.DataFrame({
        "Day": dates.strftime('%A'),
        "Max (°C)": daily["temperature_2m_max"],
        "Min (°C)": daily["temperature_2m_min"]
    })
    st.dataframe(df.set_index("Day"), use_container_width=True)

# Add this function to your script
def get_owm_forecast(city_name):
    owm_key = st.secrets.get("OPENWEATHER_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid={owm_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # Filter for 12:00 PM entries to get daily snapshots
        return [item for item in data['list'] if "12:00:00" in item['dt_txt']][:5]
    return None

# Update your tab2 block
def render_custom_bar_chart(forecast_data):
    """Renders the minimalist bar chart for temperatures."""
    dates = [d['dt_txt'].split(' ')[0] for d in forecast_data]
    temps = [d['main']['temp'] for d in forecast_data]
    
    fig = go.Figure(data=[go.Bar(
        x=dates, y=temps,
        marker_color='#E4B062',
        marker_line_width=0,
        width=0.6
    )])
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False, showticklabels=False),
        margin=dict(l=0, r=0, t=20, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

# Update your tab2 block in the script
with tab2:
    st.markdown("<h2 style='color:#FFD700;'>🔮 Extended Forecast</h2>", unsafe_allow_html=True)

    if st.session_state.w_data is not None and "daily" in st.session_state.w_data:
        render_forecast_display()
    else:
        st.warning("Primary forecast data unavailable.")
        st.markdown("---")
        st.subheader("Try Secondary Source (OpenWeatherMap)")
        manual_city = st.text_input("Enter city for OWM fallback:", key="owm_fallback_input")
        if st.button("Load via OpenWeatherMap", key="owm_load_btn"):
            with st.spinner("Querying OpenWeatherMap..."):
                forecast_data = get_owm_forecast(manual_city)
                
                if forecast_data:
                    # 1. Cards
                    cols = st.columns(5)
                    for i, day in enumerate(forecast_data):
                        with cols[i]:
                            date = day['dt_txt'].split(' ')[0]
                            temp = day['main']['temp']
                            icon = day['weather'][0]['icon']
                            st.markdown(f"""
                                <div style="text-align:center; padding:10px; background:rgba(255,255,255,0.05); border-radius:10px;">
                                    <small>{date}</small><br>
                                    <img src="http://openweathermap.org/img/wn/{icon}@2x.png" width="40"><br>
                                    <strong>{temp}°C</strong>
                                </div>
                            """, unsafe_allow_html=True)
                    
                    # 2. Add the custom chart
                    st.subheader("Temperature Trend")
                    render_custom_bar_chart(forecast_data)
                    
                    # 3. Infographic Table
                    st.subheader("Humidity & Temperature Metrics")
                    table_data = [{"Date": d['dt_txt'], "Temp (°C)": d['main']['temp'], "Humidity (%)": d['main']['humidity']} for d in forecast_data]
                    st.table(pd.DataFrame(table_data))
                else:
                    st.error("OpenWeatherMap could not find the city or API key is invalid.")
    st.markdown("<h2 style='color:#FFD700;'>💬 GeoWeather AI Assistant</h2>", unsafe_allow_html=True)
    st.caption("⚡ Powered by Gemini 3.5 Flash")
    st.markdown("---")

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # User Input
    if user_input := st.chat_input("Ask a weather query..."):
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing atmospheric data..."):
                try:
                    # Configure Gemini 3.5
                    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
                    
                    # Target the latest stable model
                    model = genai.GenerativeModel('gemini-3.5-flash')
                    
                    response = model.generate_content(user_input)
                    bot_reply = response.text
                    
                except Exception as e:
                    bot_reply = f"🚨 AI Engine Error: {str(e)}"

                st.write(bot_reply)
                st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})

# Add your existing Tab 1 and Tab 2 logic here...
