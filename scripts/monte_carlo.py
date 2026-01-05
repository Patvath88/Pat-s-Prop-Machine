import numpy as np

def monte_carlo_prob(player_df, stat, minutes, line, n=20000):
    per_min = (player_df[stat] / player_df["MIN"]).dropna()
    samples = np.random.choice(per_min, size=n, replace=True)
    sims = samples * minutes
    return np.mean(sims > line)
