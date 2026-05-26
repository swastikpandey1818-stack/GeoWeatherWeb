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
        
        /* Premium Card Containers (Glassmorphism) */
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

# Create the 3-Tab top navigation layout
tab1, tab2, tab3 = st.tabs(["📊 Live Weather Metrics", "🔮 7-Day Extended Forecast", "💬 Ask GeoWeather AI"])

# Initialize default values to avoid N/A bugs
temp_val, hum_val, wind_val = "—", "—", "—"
lat, lon = 26.7588, 83.3697 # Default to Gorakhpur coords
display_city = "Gorakhpur, Uttar Pradesh, India"

# ==========================================
# 📊 TAB 1: UPGRADED LIVE WEATHER METRICS
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
    
    if city_input:
        # 🛰️ 1. Get Coordinates using Open-Meteo Geocoding API (Free & Instant)
        try:
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_input}&count=1&language=en&format=json"
            geo_res = requests.get(geo_url).json()
            if "results" in geo_res:
                lat = geo_res["results"][0]["latitude"]
                lon = geo_res["results"][0]["longitude"]
                city_name = geo_res["results"][0]["name"]
                country = geo_res["results"][0].get("country", "")
                admin = geo_res["results"][0].get("admin1", "")
                display_city = f"{city_name}, {admin}, {country}" if admin else f"{city_name}, {country}"
            else:
                display_city = f"'{city_input}' (Using Default Coords)"
        except Exception:
            pass

        # 🌦️ 2. Fetch Actual Weather Data using Coordinates
        try:
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m&forecast_days=7"
            w_data = requests.get(weather_url).json()
            
            # Extract real API response numbers perfectly
            temp_val = f"{w_data['current']['temperature_2m']}°C"
            hum_val = f"{w_data['current']['relative_humidity_2m']}%"
            wind_val = f"{w_data['current']['wind_speed_10m']} km/h"
        except Exception as e:
            temp_val, hum_val, wind_val = "Error", "Error", "Error"

        # Render Premium Grid Layout
        st.markdown(f"### 📍 Current Analysis for **{display_city}**")
        m_col1, m_col2, m_col3 = st.columns(3)
        
        with m_col1:
            st.markdown(f"""
                <div class="weather-card" style="text-align: center;">
                    <span style="font-size: 2rem;">🌡️</span>
                    <p style="color: #888; margin: 5px 0;">Temperature</p>
                    <h2 style="margin:0; color:#FFF;">{temp_val}</h2>
                </div>
            """, unsafe_allow_html=True)
            
        with m_col2:
            st.markdown(f"""
                <div class="weather-card" style="text-align: center;">
                    <span style="font-size: 2rem;">💧</span>
                    <p style="color: #888; margin: 5px 0;">Humidity</p>
                    <h2 style="margin:0; color:#FFF;">{hum_val}</h2>
                </div>
            """, unsafe_allow_html=True)
            
        with m_col3:
            st.markdown(f"""
                <div class="weather-card" style="text-align: center;">
                    <span style="font-size: 2rem;">💨</span>
                    <p style="color: #888; margin: 5px 0;">Wind Velocity</p>
                    <h2 style="margin:0; color:#FFF;">{wind_val}</h2>
                </div>
            """, unsafe_allow_html=True)

        # Map display section
        st.markdown('### 🗺️ Geospatial Vector View')
        map_df = pd.DataFrame({'lat': [lat], 'lon': [lon]})
        st.map(map_df, zoom=10)

# ==========================================
# 🔮 TAB 2: 7-DAY EXTENDED FORECAST (DYNAMIC)
# ==========================================
with tab2:
    st.markdown("<h2 style='color:#FFD700;'>🔮 7-Day Regional Extended Forecast</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    try:
        # Pull dynamic hourly items bundled together from Open-Meteo
        hourly_df = pd.DataFrame({
            "Time": w_data["hourly"]["time"],
            "Temperature (°C)": w_data["hourly"]["temperature_2m"],
            "Humidity (%)": w_data["hourly"]["relative_humidity_2m"]
        })
        hourly_df["Time"] = pd.to_datetime(hourly_df["Time"])
        # Take daily snapshots to clean up charts
        daily_chart_data = hourly_df.resample('D', on='Time').mean().reset_index()
        daily_chart_data['Day'] = daily_chart_data['Time'].dt.strftime('%a')
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="weather-card">', unsafe_allow_html=True)
            st.subheader("📋 Weekly Temperature Curve")
            st.line_chart(daily_chart_data.set_index("Day")["Temperature (°C)"])
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="weather-card">', unsafe_allow_html=True)
            st.subheader("💧 Humidity Wave Projections")
            st.bar_chart(daily_chart_data.set_index("Day")["Humidity (%)"])
            st.markdown('</div>', unsafe_allow_html=True)
    except Exception:
        st.info("Search a city in Tab 1 to generate live data forecast lines.")

# ==========================================
# 💬 TAB 3: AI CHAT WITH AUTOMATIC FALLBACK
# ==========================================
with tab3:
    st.markdown("<h2 style='color:#FFD700;'>💬 GeoWeather AI Assistant</h2>", unsafe_allow_html=True)
    st.caption("⚡ Powered by Gemini Engine (Fallback: OpenAI GPT-4o)")
    st.markdown("---")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Namaste! I am your GeoWeather assistant. Ask me anything about local climates, forecasts, or trends!"}
        ]

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    system_rules = f"You are 'GeoWeather Pro AI', an expert meteorological intelligence assistant. The current location is {display_city} where the temp is {temp_val}. Keep answers short."

    if user_input := st.chat_input("Ask a weather query..."):
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Processing cloud queries..."):
                bot_reply = ""
                try:
                    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(f"{system_rules}\nUser Query: {user_input}")
                    bot_reply = response.text
                except Exception:
                    try:
                        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "system", "content": system_rules}, {"role": "user", "content": user_input}]
                        )
                        bot_reply = response.choices[0].message.content
                    except Exception as e:
                        bot_reply = f"🚨 AI nodes are currently busy. Local status: Temp={temp_val}, Hum={hum_val}."

                st.write(bot_reply)
                st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})