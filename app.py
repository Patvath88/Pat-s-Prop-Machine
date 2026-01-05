import streamlit as st
from expected_value import expected_stat
from probability import probability_over, implied_probability

st.set_page_config(layout="wide")
st.title("NBA Manual Prop Probability Engine")

stat_type = st.selectbox(
    "Stat Type",
    ["PTS","REB","AST","FG3M","STL","BLK","TOV"]
)

line = st.number_input("Sportsbook Line", value=20.5)
odds = st.number_input("American Odds", value=-110)

st.subheader("Projection Inputs")

col1, col2 = st.columns(2)

with col1:
    minutes = st.number_input("Projected Minutes", value=34.0)
    stat_per_min = st.number_input("Stat per Minute", value=0.75)
    recent_form = st.number_input("Recent Form Adjustment", value=1.00)
    usage_adj = st.number_input("Usage Adjustment", value=1.00)

with col2:
    opp_def_adj = st.number_input("Opponent Defense Adjustment", value=1.00)
    pace_adj = st.number_input("Pace Adjustment", value=1.00)
    home_adj = st.number_input("Home/Away Adjustment", value=1.00)

std = st.number_input(
    "Standard Deviation (Normal stats only)",
    value=4.5
)

if st.button("Calculate Probability"):

    mean = expected_stat(
        minutes,
        stat_per_min,
        recent_form,
        usage_adj,
        opp_def_adj,
        pace_adj,
        home_adj
    )

    prob_over = probability_over(mean, line, stat_type, std)
    implied = implied_probability(odds)
    edge = prob_over - implied

    st.subheader("Results")

    col1, col2, col3 = st.columns(3)

    col1.metric("Projected Mean", round(mean,2))
    col2.metric("Model Probability (Over)", f"{prob_over:.2%}")
    col3.metric("Edge", f"{edge:.2%}")
