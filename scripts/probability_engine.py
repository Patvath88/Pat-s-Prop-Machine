def implied_probability(odds):
    if odds < 0:
        return abs(odds) / (abs(odds) + 100)
    return 100 / (odds + 100)

def kelly_fraction(model_prob, odds):
    if odds < 0:
        b = 100 / abs(odds)
    else:
        b = odds / 100
    return max(0, (model_prob * (b + 1) - 1) / b)
