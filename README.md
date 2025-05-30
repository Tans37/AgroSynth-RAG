# AgroSynth-RAG

**AgroSynth-RAG** combines real-time weather alerts with a retrieval-augmented LLaMA pipeline to give farmers both immediate climate warnings and localized pest-infestation risk forecasts.

---
These are the major components in this repository:
1. weatherAlert.py: This file is used to provide real time weather alerts if in case there are any anomalies or severe weather that can potenially impact the weather.
2. query_llama_rag.py: This file utilizes a corpus of data related to Agricultural pests in New York state which includes certain open source articles, and information about the species of the pests with regards to the climatic conditions and the counties they are usually found in. We utilized Llama 3.2 and FAISS database to implement this RAG.
3. RAG Indexing: This folder contains the data(context) utilized by the RAG app and also transforming the data into vectors to implement vector search.


## 🔍 Features

- **Weather Alerts** (`weatherAlert.py` & `thresholds.js`)  
  - Heavy rain (>40 mm), flood risk, high winds (>60 km/h), frost (<5 °C) and heat (>38 °C) notifications  
  - City-to-lat/lon geocoding via Open-Meteo API  
  - Simple CLI tool (`python weatherAlert.py`)

- **Pest-Risk RAG** (`query_llama_rag.py`)  
  - FAISS-indexed pest datasheets (region → top 3 pests)  
  - 7-day forecast (GDD, humidity, rain) from Open-Meteo  
  - OpenRouter LLaMA call to answer “Will there be infestation? If yes, which pest?”  
  - Deterministic “No infestation expected.” or “Yes – <Common Name>” along with a breif generative explaination as to Why?

---

## 🚀 Getting Started

### 1. Clone & Install  
```bash
git clone https://github.com/Tans37/AgroSynth-RAG.git
cd AgroSynth-RAG
python3 -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

> **requirements.txt** should include:  
> `requests`, `fastapi`, `uvicorn`, `langchain`, `faiss-cpu`,  
> `sentence-transformers`, `openai`, `transformers`, `python-dotenv`

### 2. Configure Environment  
Create a `.env` (or set environment variables) for OpenRouter LLaMA:  
```bash
export OPENAI_API_KEY="your_openrouter_api_key"
export OPENAI_API_BASE="https://openrouter.ai/api/v1"
export OPENAI_MODEL="openrouter-llama-2-7b"
```

### 3. Run Weather Alerts  
```bash
python weatherAlert.py
# Follow the prompt to enter a city name
```

### 4. Run Pest-Risk Query  
```bash
python query_llama_rag.py
# Or integrate into FastAPI/Ngrok for React frontend:
uvicorn backend:app --reload --host 0.0.0.0 --port 8000
```

---

## 📁 Repository Structure

```
AgroSynth-RAG/
├── weatherAlert.py        # City → weather alerts CLI
├── thresholds.js          # JS constants for frontend alerts
├── query_llama_rag.py     # Script: region/crop → pest-infestation prediction
├── backend.py             # (optional) FastAPI wrapper for both flows
├── requirements.txt       # Python dependencies
└── README.md
```

---

## 🛠️ Integration

- **React Frontend**  
  - Call `/weather-alerts` (POST `{ city }`) → returns `alerts: string[]`  
  - Call `/pest-predict` (POST `{ latitude, longitude, region, crop, planting_date }`) → returns `prediction: string`  
  - Display results in your UI with buttons or map-click handlers.
