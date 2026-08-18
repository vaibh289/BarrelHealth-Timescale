MAX_ERROR = 10.0


def calculate_health(df):
    df = df.copy()

    df["temperature_error"] = (
        df["temp_actual"] - df["temp_set"]
    ).abs()

    df["health"] = (
        100 * (1 - df["temperature_error"] / MAX_ERROR)
    ).clip(0, 100)

    return df
