import joblib
from sklearn.ensemble import RandomForestRegressor

def train_minutes_model(df):
    X = df[["MIN_avg_5", "MIN_avg_10", "HOME"]]
    y = df["MIN"]

    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=8,
        random_state=42
    )

    model.fit(X, y)
    joblib.dump(model, "models/minutes_model.pkl")
