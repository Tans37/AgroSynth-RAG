import requests

# Thresholds for alerting
THRESHOLDS = {
    "rainfall": 1,        # mm
    "wind_speed": 60,      # km/h
    "frost_temp": 5,       # °C
    "high_temp": 38        # °C
}

def city_to_lat_lon(city):
    """Convert city name to lat/lon using Open-Meteo Geocoding API"""
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    try:
        res = requests.get(url).json()
        if res.get("results"):
            return res["results"][0]["latitude"], res["results"][0]["longitude"]
    except:
        pass
    return None, None

def get_daily_forecast(lat, lon):
    """Fetch daily weather forecast from Open-Meteo"""
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&daily=temperature_2m_min,temperature_2m_max,precipitation_sum,windspeed_10m_max"
        f"&timezone=auto"
    )
    try:
        res = requests.get(url)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Error fetching forecast: {e}")
        return None

def interpret_alerts(forecast):
    """Generate alert messages based on weather conditions"""
    alerts = []
    daily = forecast["daily"]

    temp_min = daily["temperature_2m_min"][0]
    temp_max = daily["temperature_2m_max"][0]
    rain = daily["precipitation_sum"][0]
    wind = daily["windspeed_10m_max"][0]

    if rain > THRESHOLDS["rainfall"]:
        alerts.append(f"🌧️ Heavy Rainfall expected (> {THRESHOLDS['rainfall']} mm).")
    if rain > 100:
        alerts.append("🌊 Possible Flood Risk due to excessive rainfall.")
    if wind > THRESHOLDS["wind_speed"]:
        alerts.append(f"🌬️ High Winds expected (> {THRESHOLDS['wind_speed']} km/h).")
    if temp_min < THRESHOLDS["frost_temp"]:
        alerts.append(f"❄️ Frost Risk: Min temp < {THRESHOLDS['frost_temp']} °C.")
    if temp_max > THRESHOLDS["high_temp"]:
        alerts.append(f"🔥 High Temperature Alert (> {THRESHOLDS['high_temp']} °C).")

    return alerts

def test_alert(city):
    lat, lon = city_to_lat_lon(city)
    if lat is None:
        print(f"❌ Could not find coordinates for {city}")
        return

    forecast = get_daily_forecast(lat, lon)
    if not forecast:
        print("❌ Failed to fetch forecast.")
        return

    alerts = interpret_alerts(forecast)
    print(f"\n📍 Location: {city}")
    print("🚨 Weather Alert for Today:" if alerts else "✅ No severe weather today.")
    for alert in alerts:
        print(" -", alert)

# Change the city here to test!
if __name__ == "__main__":
    test_city = input("Enter a city to test: ")
    test_alert(test_city)

