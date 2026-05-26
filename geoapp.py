import streamlit as st
import google.generativeai as genai
import openai
import requests
import pandas as pd

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

# Initialize Session States
if "w_data" not in st.session_state:
    st.session_state.w_data = None
if "display_city" not in st.session_state:
    st.session_state.display_city = "Gorakhpur, Uttar Pradesh, India"
if "temp_val" not in st.session_state:
    st.session_state.temp_val = "38°C"
if "hum_val" not in st.session_state:
    st.session_state.hum_val = "45%"
if "wind_val" not in st.session_state:
    st.session_state.wind_val = "14 km/h"
if "lat" not in st.session_state:
    st.session_state.lat = 26.7588
if "lon" not in st.session_state:
    st.session_state.lon = 83.3697

# Helper function to fetch data and store it cleanly in state memory
def fetch_weather_data(city_name_query):
    try:
        # Geocoding
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name_query}&count=5&language=en&format=json"
        geo_res = requests.get(geo_url).json()
        
        if "results" in geo_res and len(geo_res["results"]) > 0:
            target_result = geo_res["results"][0]
            for res in geo_res["results"]:
                if res.get("admin1") == "Uttar Pradesh":
                    target_result = res
                    break
            
            st.session_state.lat = target_result["latitude"]
            st.session_state.lon = target_result["longitude"]
            c_name = target_result["name"]
            country = target_result.get("country", "")
            admin = target_result.get("admin1", "")
            st.session_state.display_city = f"{c_name}, {admin}, {country}" if admin else f"{c_name}, {country}"
    except Exception:
        pass

    try:
        # Core Weather API call
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={st.session_state.lat}&longitude={st.session_state.lon}&current_weather=true&hourly=temperature_2m,relative_humidity_2m&daily=weathercode,temperature_2m_max,temperature_2m_min&timezone=auto&forecast_days=7"
        res_data = requests.get(weather_url).json()
        st.session_state.w_data = res_data
        
        if "current_weather" in res_data:
            st.session_state.temp_val = f"{res_data['current_weather']['temperature']}°C"
            st.session_state.wind_val = f"{res_data['current_weather']['windspeed']} km/h"
            if "hourly" in res_data:
                st.session_state.hum_val = f"{res_data['hourly']['relative_humidity_2m'][0]}%"
    except Exception:
        pass

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
    city_input = st.text_input("Enter city name:", value="Gorakhpur", placeholder="e.g., Gorakhpur, Delhi, London", label_visibility="collapsed")
    search_button = st.button("Get Live Metrics")
    st.markdown('</div>', unsafe_allow_html=True)
    
    
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
# 🔮 TAB 2: 7-DAY FORECAST WITH EMOJIS
# ==========================================
with tab2:
    st.markdown("<h2 style='color:#FFD700;'>🔮 7-Day Regional Extended Forecast</h2>", unsafe_allow_html=True)
    st.markdown("---")
    if st.session_state.w_data is not None and "daily" in st.session_state.w_data
        try:
            daily = st.session_state.w_data["daily"]
            dates = pd.to_datetime(daily["time"])
            forecast_entries = []
            
            for i in range(len(dates)):
                code = daily["weathercode"][i]
                # ... (Keep your existing emoji logic)
                if code in [0, 1]: emoji = "☀️ Sunny"
                elif code in [2, 3]: emoji = "☁️ Partly Cloudy"
                elif code in [45, 48]: emoji = "🌫️ Foggy"
                elif code in [51, 53, 55, 61, 63, 65]: emoji = "🌧️ Rainy"
                elif code in [71, 73, 75]: emoji = "❄️ Snowy"
                elif code in [95, 96, 99]: emoji = "⚡ Thunderstorm"
                else: emoji = "🌤️ Variable"
                
                forecast_entries.append({
                    "📅 Day / Date": dates[i].strftime('%A (%b %d)'),
                    "📊 Condition": emoji,
                    "🔺 Max Temp": f"{daily['temperature_2m_max'][i]}°C",
                    "🔻 Min Temp": f"{daily['temperature_2m_min'][i]}°C"
                })
            
            st.markdown('<div class="weather-card">', unsafe_allow_html=True)
            st.table(pd.DataFrame(forecast_entries).set_index("📅 Day / Date"))
            st.markdown('</div>', unsafe_allow_html=True)
            
        except Exception as e:
            # 2. Print the REAL error instead of the custom message
            st.error(f"Technical Data Error: {e}")
            st.write("Raw data sample:", st.session_state.w_data.keys())
    else:
        st.info("🔍 Loading weather data... please ensure a location is selected.")

with tab3:
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
