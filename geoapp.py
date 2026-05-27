import streamlit as st
import google.generativeai as genai
import requests
import pandas as pd
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
import pydeck as pdk

def get_weather_info(code):
    mapping = {
        0: ("Clear sky", "☀️"),
        1: ("Mainly clear", "🌤️"),
        2: ("Partly cloudy", "⛅"),
        3: ("Overcast", "☁️"),
        45: ("Fog", "🌫️"),
        48: ("Depositing rime fog", "🌫️"),
        51: ("Light drizzle", "🌦️"),
        53: ("Moderate drizzle", "🌦️"),
        55: ("Dense drizzle", "🌧️"),
        61: ("Light rain", "🌦️"),
        63: ("Moderate rain", "🌧️"),
        65: ("Heavy rain", "⛈️"),
        71: ("Light snow", "🌨️"),
        73: ("Moderate snow", "🌨️"),
        75: ("Heavy snow", "❄️"),
        80: ("Light rain showers", "🌦️"),
        81: ("Moderate rain showers", "🌧️"),
        82: ("Heavy rain showers", "⛈️"),
        95: ("Thunderstorm", "⚡"),
        96: ("Thunderstorm with hail", "⛈️"),
        99: ("Thunderstorm with heavy hail", "⛈️")
    }
    return mapping.get(code, ("Unknown", "❓"))

geolocator = Nominatim(user_agent="geoweather_app")

@st.cache_data(ttl=600)
def cached_geo_search(city_name_query):
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name_query}&count=5&language=en&format=json"
    response = requests.get(geo_url, timeout=15)
    response.raise_for_status()
    return response.json()
@st.cache_data(ttl=600)
def cached_weather_fetch(lat, lon):
    weather_url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}"
        f"&longitude={lon}&current_weather=true"
        f"&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m"
        f"&daily=weathercode,temperature_2m_max,temperature_2m_min"
        f"&timezone=auto&forecast_days=7"
    )
    response = requests.get(weather_url, timeout=15)
    response.raise_for_status()
    return response.json()

def init_app_state():
    defaults = {
        "w_data": None,
        "temp_val": "--",
        "hum_val": "--",
        "wind_val": "--",
        "display_city": "Please search for a city",
        "lat": None,
        "lon": None,
        "weather_desc": "N/A",
        "weather_emoji": "❓",
        "chat_history": []
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_app_state()

st.set_page_config(page_title="Swastik's GeoWeather Pro", page_icon="🌤️", layout="wide")

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

def fetch_weather_data(city_name_query):
    st.session_state.fetch_error = None
    
    try:
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

    try:
        res_data = cached_weather_fetch(st.session_state.lat, st.session_state.lon)
        st.session_state.w_data = res_data

        if "current_weather" in res_data:
            w_code = res_data['current_weather']['weathercode']
            desc, emoji = get_weather_info(w_code)
            st.session_state.weather_desc = desc
            st.session_state.weather_emoji = emoji
            
            st.session_state.temp_val = f"{res_data['current_weather']['temperature']}°C"
            st.session_state.wind_val = f"{res_data['current_weather']['windspeed']} km/h"
            
            if "hourly" in res_data and "relative_humidity_2m" in res_data["hourly"]:
                st.session_state.hum_val = f"{res_data['hourly']['relative_humidity_2m'][0]}%"
        else:
            st.session_state.fetch_error = "Weather data is unavailable for this location."
            
    except requests.exceptions.HTTPError as exc:
        if "429" in str(exc):
            st.session_state.fetch_error = "Too many requests to Open-Meteo. Please wait a minute and try again."
        else:
            st.session_state.fetch_error = f"Weather fetch failed: {exc}"
    except Exception as exc:
        st.session_state.fetch_error = f"Weather fetch failed: {exc}"

tab1, tab2, tab3 = st.tabs(["📊 Live Weather Metrics", "🔮 7-Day Extended Forecast", "💬 Ask GeoWeather AI"])

with tab1:
    st.markdown("""
        <div style='text-align: center; padding: 15px 0px;'>
            <h1 style='font-size: 2.5rem; margin-bottom: 0;'>🚀 <span class='gradient-text'>GeoWeather Pro</span></h1>
            <p style='color: #888888; font-size: 1rem;'>Enterprise-Grade Atmospheric Tracking Engine</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="weather-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0; font-size:1.2rem; color:#FFD700;'>🔍 Search Regional Conditions</h3>", unsafe_allow_html=True)
    city_input = st.text_input("Enter city name:", value="", placeholder="e.g., Gorakhpur, Delhi, London", label_visibility="collapsed")
    search_button = st.button("Get Live Metrics")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if search_button and city_input:
        with st.spinner(f"Fetching data for {city_input}..."):
            fetch_weather_data(city_input)
            st.rerun()
            
    if st.session_state.get("fetch_error"):
        st.error(st.session_state.fetch_error)
    
    if st.session_state.lat is not None:
        st.markdown(f"### 📍 Current Analysis for **{st.session_state.display_city}**")
        
        st.markdown(f'''
            <div class="weather-card" style="text-align: center;">
                <h2>{st.session_state.get("weather_emoji", "❓")}</h2>
                <p style="color:#888;">Condition</p>
                <h3>{st.session_state.get("weather_desc", "N/A")}</h3>
            </div>
        ''', unsafe_allow_html=True)
        
        m_col1, m_col2, m_col3 = st.columns(3)
        
        with m_col1:
            st.markdown(f'''
                <div class="weather-card" style="text-align: center;">
                    <h2>🌡️</h2><p style="color:#888;">Temperature</p>
                    <h2>{st.session_state.get("temp_val", "--")}</h2>
                </div>
            ''', unsafe_allow_html=True)

        with m_col2:
            st.markdown(f'''
                <div class="weather-card" style="text-align: center;">
                    <h2>💧</h2><p style="color:#888;">Humidity</p>
                    <h2>{st.session_state.get("hum_val", "--")}</h2>
                </div>
            ''', unsafe_allow_html=True)

        with m_col3:
            st.markdown(f'''
                <div class="weather-card" style="text-align: center;">
                    <h2>💨</h2><p style="color:#888;">Wind Velocity</p>
                    <h2>{st.session_state.get("wind_val", "--")}</h2>
                </div>
            ''', unsafe_allow_html=True)

        st.markdown('### 🗺️ Geospatial Vector View')
        st.map(pd.DataFrame({'lat': [st.session_state.lat], 'lon': [st.session_state.lon]}), zoom=10)
    else:
        st.info("Enter a city above to see live weather metrics.")

def render_forecast_display():
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


def get_owm_forecast(city_name):
    owm_key = st.secrets.get("OPENWEATHER_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid={owm_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return [item for item in data['list'] if "12:00:00" in item['dt_txt']][:5]
    return None

def render_custom_bar_chart(forecast_data):
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

with tab2:
    st.markdown("<h2 style='color:#FFD700;'>🔮 Extended Forecast</h2>", unsafe_allow_html=True)
    if st.session_state.w_data is not None and "daily" in st.session_state.w_data:
        render_forecast_display()
        
        # 1. Prepare Data
        # Get wind data (using current index [0])
        wind_spd = st.session_state.w_data["hourly"]["wind_speed_10m"][0]
        wind_dir = st.session_state.w_data["hourly"]["wind_direction_10m"][0]
        # Get temperature for heatmap (using current index [0])
        temp_val = st.session_state.w_data["hourly"]["temperature_2m"][0]
        
        # 2. Map DataFrames
        # For Heatmap
        heat_data = pd.DataFrame({'lat': [st.session_state.lat], 'lon': [st.session_state.lon], 'temp': [temp_val]})
        # For Arrow (simplified)
        arrow_data = pd.DataFrame({'lat': [st.session_state.lat], 'lon': [st.session_state.lon], 'angle': [wind_dir]})

        st.pydeck_chart(pdk.Deck(
            initial_view_state=pdk.ViewState(
                latitude=st.session_state.lat, longitude=st.session_state.lon, zoom=9, pitch=0,
            ),
           
                # Heatmap Layer
            layers=[
                # 1. Heatmap Layer (Keep it simple)
                pdk.Layer(
                    "HeatmapLayer",
                    data=heat_data,
                    get_position="[lon, lat]",
                    get_weight="temp",
                ),
                # Wind Arrow Icon Layer
                pdk.Layer(
                    "IconLayer",
                    data=arrow_data,
                    get_position="[lon, lat]",
                    # Use a simple URL string directly
                    get_icon="{'url': 'https://img.icons8.com/ios-filled/50/ffffff/long-arrow-up.png', 'width': 50, 'height': 50, 'anchorY': 25}",
                    get_size=50,
                    get_angle="angle", 
                    pickable=True,
                )
            ],
        ))
        
    else:
        # Fallback logic...
        st.warning("Primary forecast data unavailable.")
        st.markdown("---")
        st.subheader("Try Secondary Source (OpenWeatherMap)")
        manual_city = st.text_input("Enter city for OWM fallback:", key="owm_fallback_input")
        if st.button("Load via OpenWeatherMap", key="owm_load_btn"):
            with st.spinner("Querying OpenWeatherMap..."):
                forecast_data = get_owm_forecast(manual_city)
                
                if forecast_data:
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
                    
                    st.subheader("Temperature Trend")
                    render_custom_bar_chart(forecast_data)
                    
                    st.subheader("Humidity & Temperature Metrics")
                    table_data = [{"Date": d['dt_txt'], "Temp (°C)": d['main']['temp'], "Humidity (%)": d['main']['humidity']} for d in forecast_data]
                    st.table(pd.DataFrame(table_data))
                else:
                  st.error("OpenWeatherMap could not find the city or API key is invalid.")
            

with tab3:
    st.markdown("<h2 style='color:#FFD700;'>💬 GeoWeather AI Assistant</h2>", unsafe_allow_html=True)
    st.caption("⚡ Powered by Gemini 3.5 Flash")
    st.markdown("---")
    if "chat_history" not in st.session_state:
      st.session_state.chat_history = [
        {
            "role": "assistant", 
            "content": "Namaste! I'm your GeoWeather AI assistant. Ask me anything about the weather, forecasts, or atmospheric conditions in any city around the world! 🌍☁️"
        }
    ]

# 2. Loop through the list and render each message correctly
      for message in st.session_state.chat_history:
         with st.chat_message(message["role"]):
           st.write(message["content"])

    if user_input := st.chat_input("Ask a weather query..."):
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing atmospheric data..."):
                try:
                    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
                    model = genai.GenerativeModel('gemini-3.5-flash')
                    response = model.generate_content(user_input)
                    bot_reply = response.text
                except Exception as e:
                    bot_reply = f"🚨 AI Engine Error: {str(e)}"

                st.write(bot_reply)
                st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})