import os
import streamlit as st
import pandas as pd

# Import the CSV generator
from daily_player_adjustments import generate_csv

CSV_PATH = "data/daily_player_adjustments.csv"

# --- Generate CSV if missing ---
if not os.path.exists(CSV_PATH):
    st.info("Daily adjustments CSV not found. Generating now...")
    try:
        CSV_PATH = generate_csv()
        st.success("Daily adjustments CSV generated successfully!")
    except Exception as e:
        st.error(f"Failed to generate CSV: {e}")

# --- Load CSV ---
@st.cache_data
def load_data():
    if not os.path.exists(CSV_PATH):
        st.warning("Daily adjustments CSV still not found. Please check logs.")
        return pd.DataFrame()
    return pd.read_csv(CSV_PATH)

df = load_data()

st.set_page_config(layout="wide")
st.title("NBA Daily Prop Probability Engine")

if df.empty:
    st.warning("No player data available. Make sure the CSV generation succeeded.")
else:
    player_names = df['player_name'].unique()
    player_name = st.selectbox("Select Player", player_names)

    player_row = df[df['player_name'] == player_name].iloc[0]

    stat_type = st.selectbox(
        "Stat Type",
        ["PTS","REB","AST","FG3M","STL","BLK","TOV"]
    )

    line = st.number_input("Sportsbook Line", value=20.5)
    odds = st.number_input("American Odds", value=-110)

    stat_per_min_col = f"{stat_type}_per_min"
    recent_form_col = f"recent_form_{stat_type}"
    opp_def_col = f"opp_def_adj_{stat_type}"

    mean = (
        player_row['minutes_proj'] *
        player_row[stat_per_min_col] *
        player_row[recent_form_col] *
        player_row['usage_adj'] *
        player_row[opp_def_col] *
        player_row['pace_adj'] *
        player_row['home_adj']
    )

    std_default = {
        "PTS": 5, "REB": 3, "AST": 3, "FG3M": 1.5,
        "STL": 1.2, "BLK": 1.2, "TOV": 1.5
    }
    std = std_default.get(stat_type, 4)

    from scipy.stats import norm
    prob_over = 1 - norm.cdf(line, loc=mean, scale=std)

    def implied_probability(american_odds):
        if american_odds > 0:
            return 100 / (american_odds + 100)
        else:
            return -american_odds / (-american_odds + 100)

    implied = implied_probability(odds)
    edge = prob_over - implied

    st.subheader("Results")
    col1, col2, col3 = st.columns(3)
    col1.metric("Projected Mean", round(mean,2))
    col2.metric("Model Probability (Over)", f"{prob_over:.2%}")
    col3.metric("Edge vs Odds", f"{edge:.2%}")
