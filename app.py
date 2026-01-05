import streamlit as st
import pandas as pd
from expected_value import expected_stat
from probability import probability_over, implied_probability

st.set_page_config(layout="wide")
st.title("NBA Daily Prop Probability Engine")

# --- Load daily CSV ---
@st.cache_data
def load_data():
    return pd.read_csv("data/daily_player_adjustments.csv")

df = load_data()

# --- Select player ---
player_names = df['player_name'].unique()
player_name = st.selectbox("Select Player", player_names)

player_row = df[df['player_name'] == player_name].iloc[0]

stat_type = st.selectbox(
    "Stat Type",
    ["PTS","REB","AST","FG3M","STL","BLK","TOV"]
)

line = st.number_input("Sportsbook Line", value=20.5)
odds = st.number_input("American Odds", value=-110)

# --- Calculate expected stat ---
stat_per_min_col = f"{stat_type}_per_min"
recent_form_col = f"recent_form_{stat_type}"

mean = expected_stat(
    minutes_proj=player_row['minutes_proj'],
    stat_per_min=player_row[stat_per_min_col],
    recent_form_adj=player_row[recent_form_col],
    usage_adj=player_row['usage_adj'],
    opp_def_adj=player_row['opp_def_adj'],
    pace_adj=player_row['pace_adj'],
    home_adj=player_row['home_adj']
)

std_default = {
    "PTS": 5,
    "REB": 3,
    "AST": 3,
    "FG3M": 1.5,
    "STL": 1.2,
    "BLK": 1.2,
    "TOV": 1.5
}

std = std_default.get(stat_type, 4)

prob_over = probability_over(mean, line, stat_type, std)
implied = implied_probability(odds)
edge = prob_over - implied

st.subheader("Results")
col1, col2, col3 = st.columns(3)
col1.metric("Projected Mean", round(mean,2))
col2.metric("Model Probability (Over)", f"{prob_over:.2%}")
col3.metric("Edge vs Odds", f"{edge:.2%}")
