from geopy.geocoders import Nominatim
import requests
import streamlit as st
import streamlit.components.v1 as components

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
    
    st.subheader(f"**Weather Information for {input_city.title()}:**")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Temperature (°C)", value=f"{data['current']['temperature_2m']} °C")
        st.metric(label="**wind speed (km/h)**", value=f"{data['current']['windspeed_10m']} km/h")

        
    with col2:
        st.metric(label="**Relative Humidity (%)**", value=f"{data['current']['relative_humidity_2m']} %")
        st.metric(label="**Weather Condition**", value=get_weather_desc(data['current']['weathercode']))
    

    st.write(f"**Coordinates:** Latitude {latitude}, Longitude {longitude}")
    st.write("**This Website is Made by Swatik Pandey**")
   
    
    # --- ADDING THE GOOGLE MAPS SATELLITE VIEW ---
    st.markdown("### 🛰️ **Satellite View**")
    
    # Create the Google Maps Embed URL using the latitude and longitude
    # 't=k' sets the map type to Satellite/Terrain mode
    google_maps_url = f"https://maps.google.com/maps?q={latitude},{longitude}&t=k&z=12&output=embed"
    
    # Embed it cleanly using HTML components
    
    components.html(
        f'<iframe src="{google_maps_url}" width="100%" height="400" style="border:0; border-radius:10px;" allowfullscreen="" loading="lazy"></iframe>',
        height=410
    )


    # Updated URL to include BOTH current data AND 7-day daily forecast parameters
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,weathercode,windspeed_10m,relative_humidity_2m&daily=weathercode,temperature_2m_max,temperature_2m_min&timezone=auto"

    # Make the request
    response = requests.get(url)
    data = response.json()
    
    # 1. Display Current Weather

    
    # 2. Display 7-Day Forecast Section
    st.markdown("### 📅 **7-Day Forecast**")
    
    daily_data = data['daily']
    dates = daily_data['time']
    max_temps = daily_data['temperature_2m_max']
    min_temps = daily_data['temperature_2m_min']
    weather_codes = daily_data['weathercode']
    
    # Create 7 responsive layout columns side-by-side
    forecast_cols = st.columns(7)
    
    for i in range(7):
        with forecast_cols[i]:
            # Format the date string (YYYY-MM-DD) to look cleaner (e.g., May 25)
            import datetime
            date_obj = datetime.datetime.strptime(dates[i], "%Y-%m-%d")
            day_name = date_obj.strftime("%a")  # e.g., Mon, Tue
            day_date = date_obj.strftime("%b %d") # e.g., May 25
            
            # Extract emoji icon from your mapping function
            condition_desc = get_weather_desc(weather_codes[i])
            emoji = condition_desc.split()[-1] if len(condition_desc.split()) > 0 else "🌡️"
            
            # Render the forecast card
            st.markdown(f"**{day_name}**")
            st.caption(day_date)
            st.markdown(f"### {emoji}")
            st.markdown(f"🔥**{int(max_temps[i])}°**")
            st.markdown(f"❄️**{int(min_temps[i])}°**")

if button:
    latitude, longitude = longitude_latitude(input_city)
    if latitude and longitude:
        get_weather(latitude, longitude)
