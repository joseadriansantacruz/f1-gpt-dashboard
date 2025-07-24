
import streamlit as st
import pandas as pd
import fastf1
import os

# Enable FastF1 cache with directory check
os.makedirs('/tmp/f1cache', exist_ok=True)
fastf1.Cache.enable_cache('/tmp/f1cache')

# Page setup
st.set_page_config(page_title="F1 Live Dashboard", layout="wide")

# Sidebar - session and toggle options
st.sidebar.header("Session Controls")
year = st.sidebar.selectbox("Select Year", list(range(2025, 2015, -1)))
events = fastf1.get_event_schedule(year)
gp_names = events[~events['EventName'].str.contains("Testing", case=False)]['EventName']
selected_event_name = st.sidebar.selectbox("Select Grand Prix", gp_names)
session_type = st.sidebar.radio("Session", ["Practice 1", "Practice 2", "Practice 3", "Qualifying", "Race"])
gpt_enabled = st.sidebar.checkbox("Enable GPT-4 Commentary", value=False)
max_gpt_calls = st.sidebar.slider("Max GPT Commentary Calls", min_value=1, max_value=20, value=5)

# Mapping session type to FastF1 code
session_map = {"Practice 1": 'FP1', "Practice 2": 'FP2', "Practice 3": 'FP3', "Qualifying": 'Q', "Race": 'R'}
session_code = session_map[session_type]
event_data = events.loc[events['EventName'] == selected_event_name].iloc[0]
event_round = event_data['RoundNumber']
country = event_data['Country']
country_flag = {
    "Italy": "🇮🇹", "United Kingdom": "🇬🇧", "USA": "🇺🇸", "Canada": "🇨🇦", "Australia": "🇦🇺",
    "Mexico": "🇲🇽", "Brazil": "🇧🇷", "France": "🇫🇷", "Germany": "🇩🇪", "Japan": "🇯🇵",
    "Spain": "🇪🇸", "Austria": "🇦🇹", "Netherlands": "🇳🇱", "Belgium": "🇧🇪", "Singapore": "🇸🇬",
    "Saudi Arabia": "🇸🇦", "Qatar": "🇶🇦", "China": "🇨🇳", "Hungary": "🇭🇺", "Monaco": "🇲🇨"
}.get(country, "")

# Dynamic Page Title
st.title(f"{year} {selected_event_name} – {session_type} {country_flag}")

# Load session and handle missing data gracefully
try:
    session = fastf1.get_session(year, int(event_round), session_code)
    session.load()

    if session.laps.empty:
        st.warning("No lap data available for this session. Try selecting a different driver or session.")
    else:
        laps = session.laps
        drivers = sorted(laps['Driver'].unique())
        driver = st.selectbox("Select Driver", drivers)

        driver_laps = laps.pick_driver(driver)
        if driver_laps.empty:
            st.warning(f"No lap data found for {driver} in this session.")
        else:
            st.subheader(f"Lap Times - {driver}")
            try:
                lap_df = driver_laps[["LapNumber", "LapTime", "Compound", "TyreLife", "PitOutTime", "PitInTime"]]

                # Format times properly
                def format_laptime(t):
                    if pd.isnull(t):
                        return "N/A"
                    total_seconds = t.total_seconds()
                    minutes = int(total_seconds // 60)
                    seconds = total_seconds % 60
                    return f"{minutes}:{seconds:06.3f}"  # e.g. 1:23.456

                lap_df["LapTime"] = lap_df["LapTime"].apply(format_laptime)
                lap_df["PitOutTime"] = lap_df["PitOutTime"].apply(format_laptime)
                lap_df["PitInTime"] = lap_df["PitInTime"].apply(format_laptime)

                st.dataframe(lap_df.fillna("N/A"))

                if gpt_enabled:
                    st.markdown("### 🤖 GPT-4 Commentary")
                    gpt_counter = 0
                    for i in range(min(max_gpt_calls, len(lap_df))):
                        st.info(f"Lap {lap_df.iloc[i]['LapNumber']}: {driver} set a time of {lap_df.iloc[i]['LapTime']} on {lap_df.iloc[i]['Compound']} tires.")
                        gpt_counter += 1
                    st.success(f"Total GPT commentary calls used: {gpt_counter} / {max_gpt_calls}")
                else:
                    st.warning("GPT Commentary is disabled. Enable it in the sidebar.")
            except Exception as lap_error:
                st.error(f"Unable to display lap data: {lap_error}")
except Exception as e:
    st.error(f"Error loading session: {e}")
