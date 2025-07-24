
# 🏎️ F1 Dashboard with GPT Commentary

This Streamlit app displays F1 session data (Practice, Qualifying, Race) using FastF1 and includes optional GPT-4 commentary.

## Features
- Live or historical session data
- Lap-by-lap breakdown per driver
- GPT-4 commentary toggle and usage limiter
- Deployed via Streamlit Cloud (free)

## Setup
1. Clone this repo
2. Install requirements: `pip install -r requirements.txt`
3. Run: `streamlit run app.py`

## GPT API Key
To enable GPT-4 commentary:
- Add your OpenAI key via environment variable: `OPENAI_API_KEY`
