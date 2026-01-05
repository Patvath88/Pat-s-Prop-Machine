import streamlit as st
import pandas as pd
import joblib
import numpy as np
import matplotlib.pyplot as plt

from scripts.probability_engine import (
    implied_probability,
    kelly_fraction
)
from scripts.monte_carlo import monte_carlo_prob

st.set_page_config(page_title="NBA Prop Betting Engine", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("data/processed/model_data.csv")

@st.cache_resource
def load_models():
    stat_model = joblib.load("models/nba_stat_model.pkl")
    min_model = joblib.load("models/minutes_model.pkl")
    return stat_model, min_model

df = load_data()
stat_model, min_model = load_models()

TARGETS = ["PTS", "REB", "AST", "FG3M", "STL", "BLK", "TOV"]

st.title("NBA Player Prop Probability Engine")

# ---------------- SIDEBAR ----------------
st.sidebar.header("Prop Inputs")

player = st.sidebar.selectbox(
    "Player",
    sorted(df["PLAYER_NAME"].unique())
)

stat = st.sidebar.selectbox("Stat", TARGETS)
line = st.sidebar.number_input("Prop Line", value=20.5)
odds = st.sidebar.number_input("Odds (American)", value=-110)

player_df = df[df["PLAYER_NAME"] == player].sort_values("GAME_DATE")
latest = player_df.tail(1)

# ---------------- MINUTES ----------------
min_features = latest[["MIN_avg_5", "MIN_avg_10", "HOME"]]
expected_minutes = min_model.predict(min_features)[0]

# ---------------- STAT PROJECTION ----------------
X_latest = latest.drop(
    columns=TARGETS + ["GAME_DATE", "MATCHUP", "PLAYER_NAME"]
)

mu = stat_model.predict(X_latest)[0][TARGETS.index(stat)]

# ---------------- PROBABILITY ----------------
model_prob = monte_carlo_prob(
    player_df,
    stat,
    expected_minutes,
    line
)

book_prob = implied_probability(odds)
edge = model_prob - book_prob
kelly = kelly_fraction(model_prob, odds) * 0.5  # half Kelly

# ---------------- DISPLAY METRICS ----------------
c1, c2, c3, c4 = st.columns(4)

c1.metric("Projected Mean", f"{mu:.2f}")
c2.metric("Model Probability", f"{model_prob:.1%}")
c3.metric("Edge", f"{edge:.1%}")
c4.metric("Kelly %", f"{kelly:.1%}")

# ---------------- VERDICT ----------------
if edge > 0.05:
    st.success("STRONG +EV BET")
elif edge > 0.03:
    st.info("PLAYABLE EDGE")
else:
    st.error("NO BET")

# ---------------- DISTRIBUTION ----------------
st.subheader("Monte Carlo Distribution")

sims = []
per_min = (player_df[stat] / player_df["MIN"]).dropna()
samples = np.random.choice(per_min, size=5000, replace=True)
sims = samples * expected_minutes

fig, ax = plt.subplots()
ax.hist(sims, bins=40)
ax.axvline(line)
st.pyplot(fig)

# ---------------- RECENT GAMES ----------------
st.subheader("Last 10 Games")
st.dataframe(
    player_df.tail(10)[
        ["GAME_DATE", "MIN"] + TARGETS
    ],
    use_container_width=True
)
