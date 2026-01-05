from scipy.stats import norm, poisson

def probability_over(mean, line, stat_type, std=None):

    if stat_type in ["PTS","REB","AST"]:
        return 1 - norm.cdf(line, mean, std)

    else:
        return 1 - poisson.cdf(line, mean)


def implied_probability(odds):
    if odds < 0:
        return abs(odds) / (abs(odds) + 100)
    else:
        return 100 / (odds + 100)
