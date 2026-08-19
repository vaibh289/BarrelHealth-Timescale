from pathlib import Path
import re

import pandas as pd

from database import initialize_database, write_readings

DATA_FILE = Path(__file__).parent / "data" / "new_data.tsv"


def clock_to_seconds(value):
    if pd.isna(value) or str(value).strip().upper() in {"", "NULL", "NAN"}:
        return None

    match = re.fullmatch(r"(\d+):(\d+)(?:\.(\d+))?", str(value).strip())
    if not match:
        raise ValueError(f"Unsupported time value: {value!r}")

    minutes = int(match.group(1))
    seconds = int(match.group(2))
    fraction = int((match.group(3) or "0")[:3].ljust(3, "0"))

    return minutes * 60 + seconds + fraction / 1000


def prepare_data():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Data file not found: {DATA_FILE}"
        )

    # The file has a .tsv extension but is actually comma-separated.
    df = pd.read_csv(DATA_FILE)

    required = {
        "machine_time",
        "heater_time",
        "zone",
        "temp_actual",
        "temp_set",
        "hdc",
        "health",
        "cause",
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    # Convert elapsed clock values to seconds.
    df["machine_elapsed_seconds"] = df["machine_time"].apply(
        clock_to_seconds
    )

    df["heater_elapsed_seconds"] = df["heater_time"].apply(
        clock_to_seconds
    )

    # Convert numeric values.
    df["temp_actual"] = pd.to_numeric(
        df["temp_actual"],
        errors="coerce",
    )

    df["temp_set"] = pd.to_numeric(
        df["temp_set"],
        errors="coerce",
    )

    df["hdc"] = pd.to_numeric(
        df["hdc"],
        errors="coerce",
    )

    # Database calls this source_health; input file calls it health.
    df["source_health"] = pd.to_numeric(
        df["health"],
        errors="coerce",
    )

    df["zone"] = df["zone"].astype(str)

    df["cause"] = df["cause"].replace(
        {"NULL": None, "nan": None}
    )

    # Anchor elapsed machine time to today's UTC date.
    base_date = pd.Timestamp.now(tz="UTC").normalize()

    df["time"] = base_date + pd.to_timedelta(
        df["machine_elapsed_seconds"],
        unit="s",
    )

    return df


if __name__ == "__main__":
    initialize_database()

    df = prepare_data()

    print(f"Prepared {len(df)} rows.")
    print(df.head())

    write_readings(df)

    print("Import completed successfully.")