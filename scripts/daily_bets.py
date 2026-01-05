def generate_bets(df):
    bets = df[
        (df["EDGE"] > 0.03) &
        (df["KELLY"] > 0)
    ].sort_values("EDGE", ascending=False)

    bets.to_csv("data/daily_bets.csv", index=False)
