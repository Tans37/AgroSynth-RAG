import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["OPENAI_API_KEY"]  = "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"
os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"

import openai


import datetime
import requests

from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
import openai

# ——— Setup OpenRouter (LLaMA) ———
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = os.getenv("OPENAI_API_BASE")

MODEL_NAME = "meta-llama/llama-3.3-8b-instruct:free"   # or whatever your OpenRouter LLaMA model is called

# ——— Load your FAISS index ———
embed      = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
faiss_index = FAISS.load_local("faiss_pest_index", embed, allow_dangerous_deserialization=True)

# ——— Utility functions (weather + GDD) ———
def fetch_weather(lat: float, lon: float) -> dict:
    """
    Fetch a 7-day forecast:
     - daily: temperature_2m_max, temperature_2m_min, precipitation_sum
     - hourly: relativehumidity_2m
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&timezone=auto&forecast_days=7"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
        f"&hourly=relativehumidity_2m"
    )
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    return {
        "daily": data["daily"],
        "hourly": data["hourly"],
    }

def compute_gdd(tmax, tmin, base_temp=10.0):
    gdd = 0.0
    for hi, lo in zip(tmax, tmin):
        avg = (hi + lo)/2
        if avg > base_temp:
            gdd += (avg - base_temp)
    return gdd

# ——— RAG + OpenRouter call ———
def rag_with_openrouter(lat, lon, region, crop, planting_date):
    # 1. Retrieve top-3 docs
    docs    = faiss_index.similarity_search(region, k=3)
    context = "\n\n".join(d.page_content for d in docs)

    # 2. Get weather & compute features
    weather  = fetch_weather(lat, lon)
    tmax = weather["daily"]["temperature_2m_max"]
    tmin = weather["daily"]["temperature_2m_min"]
    rain = weather["daily"]["precipitation_sum"]
    humidity = weather["hourly"]["relativehumidity_2m"][-1]
    #rain     = weather["precipitation_sum"][-1]
    gdd      = compute_gdd(tmax, tmin)

    # 3. Build the prompt
    prompt = f"""
You are an expert agronomist. Here are the relevant pest datasheets:
{context}

A grower planted {crop} on {planting_date} at {region}.
The 7-day forecast yields:
  • Cumulative GDD = {gdd:.1f}
  • Humidity = {humidity}%
  • Rainfall = {rain} mm

Question:
Will there be any pest infestation possible in the next 7 days?
• If **no**, reply: “No infestation expected.”
• If **yes**, reply: "Caution!!! Infestation Expected: name the pest species if present in the data else say No infestation expected, probability(%)".
Answer only in one line, dont say anything after giving the probability.
"""

    # 4. Call OpenRouter via the OpenAI client
    resp = openai.ChatCompletion.create(
        model=MODEL_NAME,
        messages=[{"role":"user","content": prompt}],
        temperature=0.33,
        max_tokens=40,
    )
    return resp.choices[0].message.content.strip()

from geopy.geocoders import Nominatim

def lookup_region(lat, lon):
    geolocator = Nominatim(user_agent="pest_rag_app")
    loc = geolocator.reverse((lat, lon), language="en")
    return loc.raw["address"].get("county") 


# ——— Example ———
if __name__ == "__main__":
    region = lookup_region(42.5, -73.8)
    print(f"Region: {region}")
    out = rag_with_openrouter(
        lat=42.5,
        lon=-73.8,
        region=region,
        crop="Cabbage",
        planting_date=datetime.date(2025,5,1)
    )
    print(out)
