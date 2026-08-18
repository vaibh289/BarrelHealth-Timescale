import joblib
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

MODEL_FILE = "barrel_health_model.pkl"


def train_model(df):

    work = df.dropna(
        subset=[
            "hdc",
            "machine_elapsed_seconds",
            "heater_elapsed_seconds",
            "temp_actual",
            "temp_set",
            "health",
        ]
    ).copy()

    print("\nHEALTH DISTRIBUTION")
    print(
        work.groupby("zone")["health"]
        .agg(["count", "min", "max", "mean"])
        .round(2)
    )

    # ------------------------------------------
    # FEATURES
    # ------------------------------------------

    X = work[
        [
            "hdc",
            "machine_elapsed_seconds",
            "heater_elapsed_seconds",
            "temp_actual",
            "temp_set",
            "zone",
        ]
    ].copy()

    X = pd.get_dummies(
        X,
        columns=["zone"],
        dtype=int
    )

    y = work["health"]

    if len(work) < 10:
        raise ValueError(
            "At least 10 usable rows are needed to train the model."
        )

    # ------------------------------------------
    # TRAIN / TEST SPLIT
    # ------------------------------------------

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
    )

    # ------------------------------------------
    # RANDOM FOREST
    # ------------------------------------------

    model = RandomForestRegressor(
        n_estimators=300,
        random_state=42,
        max_depth=8,
        min_samples_leaf=2,
        n_jobs=-1,
    )

    model.fit(X_train, y_train)

    # ------------------------------------------
    # TEST SET EVALUATION
    # ------------------------------------------

    test_pred = (
        model.predict(X_test)
        .clip(0, 100)
    )

    print("\nRANDOM FOREST")
    print(f"Training samples: {len(X_train)}")
    print(f"Testing samples : {len(X_test)}")

    print(
        f"MAE             : "
        f"{mean_absolute_error(y_test, test_pred):.4f}"
    )

    print(
        f"RMSE            : "
        f"{mean_squared_error(y_test, test_pred) ** 0.5:.4f}"
    )

    print(
        f"R2              : "
        f"{r2_score(y_test, test_pred):.4f}"
    )

    # ------------------------------------------
    # PREDICT ALL RECORDS
    #
    # These are useful for displaying the
    # historical dataset, but should NOT be
    # considered a test-set metric.
    # ------------------------------------------

    work["Predicted_Health"] = (
        model.predict(X)
        .clip(0, 100)
        .round(2)
    )

    work["Residual"] = (
        work["health"] -
        work["Predicted_Health"]
    ).round(2)

    # ------------------------------------------
    # STATUS
    # ------------------------------------------

    work["Status"] = work["Predicted_Health"].apply(
        lambda x:
            "Healthy" if x >= 90 else
            "Warning" if x >= 75 else
            "Critical" if x >= 60 else
            "Immediate Maintenance"
    )

    # ------------------------------------------
    # SAVE MODEL
    # ------------------------------------------

    joblib.dump(
        {
            "model": model,
            "features": X.columns.tolist(),
        },
        MODEL_FILE,
    )

    print(f"\nModel saved to {MODEL_FILE}")

    return work