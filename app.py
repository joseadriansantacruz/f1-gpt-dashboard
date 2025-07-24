
import streamlit as st
import pandas as pd
import fastf1
from fastf1 import plotting
from openai import OpenAI
import os

# Enable FastF1 cache
fastf1.Cache.enable_cache('/tmp/f1cache')

# Page setup
st.set_page_config(page_title="F1 Live Dashboard", layout="wide")
st.title("🏎️ Formula 1 Dashboard with GPT Commentary")

# Sidebar - session and toggle options
st.sidebar.header("Session Controls")
year = st.sidebar.selectbox("Select Year", list(range(2025, 2015, -1)))
events = fastf1.get_event_schedule(year)
gp_names = events['EventName']
selected_event_name = st.sidebar.selectbox("Select Grand Prix", gp_names)
session_type = st.sidebar.radio("Session", ["Practice 1", "Practice 2", "Practice 3", "Qualifying", "Race"])
gpt_enabled = st.sidebar.checkbox("Enable GPT-4 Commentary", value=False)
max_gpt_calls = st.sidebar.slider("Max GPT Commentary Calls", min_value=1, max_value=20, value=5)

# Mapping session type to FastF1 code
session_map = {"Practice 1": 'FP1', "Practice 2": 'FP2', "Practice 3": 'FP3', "Qualifying": 'Q', "Race": 'R'}
session_code = session_map[session_type]
event_round = events.loc[events['EventName'] == selected_event_name]['RoundNumber'].values[0]

# Load session
try:
    session = fastf1.get_session(year, int(event_round), session_code)
    session.load()
    st.success(f"{session_type} loaded for {selected_event_name}")
    laps = session.laps
    drivers = sorted(laps['Driver'].unique())
    driver = st.selectbox("Select Driver", drivers)
    driver_laps = laps.pick_driver(driver)

    st.subheader(f"Lap Times - {driver}")
    lap_df = driver_laps[["LapNumber", "LapTime", "Compound", "TyreLife", "PitOutTime", "PitInTime"]].dropna()
    st.dataframe(lap_df)

    if gpt_enabled:
        st.markdown("### 🤖 GPT-4 Commentary")
        # Placeholder commentary logic (mocked)
        gpt_counter = 0
        for i in range(min(max_gpt_calls, len(lap_df))):
            st.info(f"Lap {lap_df.iloc[i]['LapNumber']}: {driver} set a time of {lap_df.iloc[i]['LapTime']} on {lap_df.iloc[i]['Compound']} tires.")
            gpt_counter += 1

        st.success(f"Total GPT commentary calls used: {gpt_counter} / {max_gpt_calls}")
    else:
        st.warning("GPT Commentary is disabled. Enable it in the sidebar.")

except Exception as e:
    st.error(f"Error loading session: {e}")
