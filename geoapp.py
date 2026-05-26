import datetime
import requests
import streamlit as st
import streamlit.components.v1 as components
from geopy.geocoders import Nominatim
import pandas as pd
import google.generativeai as genai

# 1. Page Configuration Setup
st.set_page_config(
    page_title="Swastik GeoWeather - Live Weather App",
    page_icon="⚡",
    layout="wide", # Adjusted to wide to let premium card grids look uniform on desktops
    initial_sidebar_state="collapsed"
)

# 💎 PREMIUM GLOBAL CSS CUSTOMIZATIONS
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght=300;400;600;700&display=swap');

        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Inter', sans-serif;
            background-color: #0E1117;
            color: #E0E0E0;
        }

        [data-testid="stHeader"] {
            background: rgba(0,0,0,0);
        }
        
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
            background: linear-gradient(45deg, #FFD700, #FFA500);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
            display: inline-block;
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

# Navigation Layout Instantiation
tab1, tab2, tab3 = st.tabs(["📊 Live Weather Metrics", "🔮 7-Day Extended Forecast", "💬 Ask GeoWeather AI"])

# Global Setup Initialization for Geolocation Engine
geolocator = Nominatim(user_agent="geoweather_pro_app")

# ==========================================
# 📊 TAB 1: LIVE WEATHER METRICS
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
    city_input = st.text_input("Enter city name:", placeholder="e.g., Gorakhpur, Delhi, London", label_visibility="collapsed")
    search_button = st.button("Get Live Metrics")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if city_input:
        try:
            # Connect live to Geopy locator map vectors
            location = geolocator.geocode(city_input, timeout=10)
            if location:
                lat, lon = location.latitude, location.longitude
                
                # Fetch instant accurate atmospheric vectors using Open-Meteo free engine tier
                api_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m&daily=temperature_2m_max,temperature_2m_min,relative_humidity_2m_mean&timezone=auto"
                response = requests.get(api_url).json()
                
                current_data = response.get("current", {})
                temp = current_data.get("temperature_2m", "N/A")
                humidity = current_data.get("relative_humidity_2m", "N/A")
                wind = current_data.get("wind_speed_10m", "N/A")
                
                st.markdown(f"### 📍 Current Analysis for **{location.address}**")
                
                # Render responsive HTML blocks containing dynamic variable properties
                m_col1, m_col2, m_col3 = st.columns(3)
                with m_col1:
                    st.markdown(f"""
                        <div class="weather-card" style="text-align: center;">
                            <span style="font-size: 2rem;">🌡️</span>
                            <p style="color: #888; margin: 5px 0;">Temperature</p>
                            <h2 style="margin:0; color:#FFF;">{temp}°C</h2>
                        </div>
                    """, unsafe_allow_html=True)
                with m_col2:
                    st.markdown(f"""
                        <div class="weather-card" style="text-align: center;">
                            <span style="font-size: 2rem;">💧</span>
                            <p style="color: #888; margin: 5px 0;">Humidity</p>
                            <h2 style="margin:0; color:#FFF;">{humidity}%</h2>
                        </div>
                    """, unsafe_allow_html=True)
                with m_col3:
                    st.markdown(f"""
                        <div class="weather-card" style="text-align: center;">
                            <span style="font-size: 2rem;">💨</span>
                            <p style="color: #888; margin: 5px 0;">Wind Velocity</p>
                            <h2 style="margin:0; color:#FFF;">{wind} km/h</h2>
                        </div>
                    """, unsafe_allow_html=True)
                
                # 🗺️ Embedded OpenStreetMap Dynamic Frame block
                st.markdown('<div class="weather-card">', unsafe_allow_html=True)
                st.markdown("<h4 style='margin-top:0; color:#FFD700;'>🗺️ Geospatial Vector View</h4>", unsafe_allow_html=True)
                map_html = f"""
                <iframe width="100%" height="350" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" 
                src="https://www.openstreetmap.org/export/embed.html?bbox={lon-0.1}%2C{lat-0.1}%2C{lon+0.1}%2C{lat+0.1}&amp;layer=mapnik&amp;marker={lat}%2C{lon}">
                </iframe>
                """
                components.html(map_html, height=360)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Store coordinates inside execution state cache for Tab 2 reference maps
                st.session_state['last_weather_data'] = response

            else:
                st.error("❌ Specified global region bounds not discovered. Please recheck city name syntax.")
        except Exception as err:
            st.error(f"⚠️ Atmospheric data pipeline link timed out: {err}")

# ==========================================
# 🔮 TAB 2: 7-DAY EXTENDED FORECAST
# ==========================================
with tab2:
    st.markdown("<h2 style='color:#FFD700;'>🔮 7-Day Regional Extended Forecast</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Verify if active target coordinates cache layer parameters are stored
    if 'last_weather_data' in st.session_state:
        weather_json = st.session_state['last_weather_data']
        daily_raw = weather_json.get("daily", {})
        
        # Parse arrays dynamically from API timeline indices
        date_strings = daily_raw.get("time", [])
        days_transformed = [datetime.datetime.strptime(d, "%Y-%m-%d").strftime("%a") for d in date_strings]
        
        forecast_df = pd.DataFrame({
            "Day": days_transformed,
            "Max Temp (°C)": daily_raw.get("temperature_2m_max", []),
            "Min Temp (°C)": daily_raw.get("temperature_2m_min", []),
            "Avg Humidity (%)": daily_raw.get("relative_humidity_2m_mean", [])
        })
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="weather-card">', unsafe_allow_html=True)
            st.subheader("📋 Core Temperature Bounds")
            st.line_chart(forecast_df.set_index("Day")[["Max Temp (°C)", "Min Temp (°C)"]])
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="weather-card">', unsafe_allow_html=True)
            st.subheader("💧 Humidity Percentage Projections")
            st.bar_chart(forecast_df.set_index("Day")["Avg Humidity (%)"])
            st.markdown('</div>', unsafe_allow_html=True)
            
        # Display raw data table view below metrics
        with st.expander("👁️ View Full Spreadsheet Forecast Matrices"):
            st.dataframe(forecast_df, use_container_width=True)
    else:
        st.info("ℹ️ Please enter and process a location query inside Tab 1 first to load extended charts.")

# ==========================================
# 💬 TAB 3: AI CHAT WITH FALLBACK
# ==========================================
with tab3:
    st.markdown("<h2 style='color:#FFD700;'>💬 GeoWeather AI Assistant</h2>", unsafe_allow_html=True)
    st.caption("⚡ Powered by Gemini Engine")
    st.markdown("---")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Namaste! I am your GeoWeather assistant. Ask me anything about local climates, forecasts, or trends!"}
        ]

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    system_rules = "You are 'GeoWeather Pro AI', an expert meteorological intelligence assistant. Answer briefly."

    if user_input := st.chat_input("Ask a weather query..."):
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Processing atmospheric cloud queries..."):
                bot_reply = ""
                try:
                    # Pointing to Gemini API Key stored safely inside cloud environment
                    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(f"{system_rules}\nUser Query: {user_input}")
                    bot_reply = response.text
                except Exception as e:
                    bot_reply = f"🚨 System pipeline busy or API key configuration missing. Details: {e}"

                st.write(bot_reply)
                st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})