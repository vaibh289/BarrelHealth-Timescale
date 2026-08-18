import pandas as pd
import numpy as np

from database import load_readings, write_predictions
from health import calculate_health
from model import train_model
from utils import status

CRITICAL_HEALTH = 50


def estimate_time_to_critical(df, zone, window=20):
    zone_df = df[df["zone"] == zone].copy()

    if len(zone_df) < 3:
        return None

    recent = zone_df.tail(min(window, len(zone_df)))

    time_minutes = (
        recent["time"] - recent["time"].iloc[0]
    ).dt.total_seconds() / 60

    health = recent["health"].values

    if len(set(health)) < 2:
        return None

    slope, intercept = np.polyfit(
        time_minutes.values,
        health,
        1
    )

    current_health = health[-1]

    if current_health <= CRITICAL_HEALTH:
        return 0.0

    if slope >= 0:
        return None

    minutes_remaining = (
        CRITICAL_HEALTH - current_health
    ) / slope

    if minutes_remaining < 0:
        return None

    return round(minutes_remaining / 60, 1)


# ==========================================
# LOAD DATA FROM TIMESCALEDB
# ==========================================

print("\nLoading readings from TimescaleDB...")

df = load_readings()

print(f"Rows loaded: {len(df)}")


# ==========================================
# RENAME DATABASE COLUMNS
# ==========================================

df["machine_minutes"] = (
    df["machine_elapsed_seconds"] / 60
)

df["heater_minutes"] = (
    df["heater_elapsed_seconds"] / 60
)


# ==========================================
# CALCULATE HEALTH
# ==========================================

df = calculate_health(df)


# ==========================================
# RANDOM FOREST
# ==========================================

df = train_model(df)


# ==========================================
# STATUS
# ==========================================

df["Status"] = df["health"].apply(status)


# ==========================================
# SAVE PREDICTIONS TO TIMESCALEDB
# ==========================================

prediction_df = df.rename(
    columns={
        "time": "time",
        "health": "actual_health",
        "Predicted_Health": "predicted_health",
        "Residual": "residual",
        "Status": "status",
    }
)

write_predictions(
    prediction_df[
        [
            "time",
            "zone",
            "actual_health",
            "predicted_health",
            "residual",
            "status",
        ]
    ]
)


# ==========================================
# LATEST READING PER ZONE
# ==========================================

latest_by_zone = (
    df.groupby("zone", sort=False)
      .tail(1)
)


# ==========================================
# PRINT REPORT
# ==========================================

print("\n==============================================")
print("       BARREL HEALTH - ALL ZONES")
print("==============================================")


for _, row in latest_by_zone.iterrows():

    print("\n----------------------------------------------")
    print(f"ZONE: {row['zone']}")
    print("----------------------------------------------")

    print(f"Time               : {row['time']}")

    print(
        f"Temperature Set    : {row['temp_set']:.2f}"
    )

    print(
        f"Temperature Actual : {row['temp_actual']:.2f}"
    )

    print(
        f"Temperature Error  : {row['temperature_error']:.2f}"
    )

    print(
        f"HDC                : {row['hdc']:.2f}"
    )

    print(
        f"Actual Health      : {row['health']:.2f}%"
    )

    print(
        f"Predicted Health   : {row['Predicted_Health']:.2f}%"
    )

    print(
        f"Residual           : {row['Residual']:.2f}"
    )

    print(
        f"Status             : {row['Status']}"
    )


print("\n==============================================")
print("Predictions saved to TimescaleDB")
print("==============================================")