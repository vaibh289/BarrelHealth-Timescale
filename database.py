import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://barreluser:barrelpass@127.0.0.1:5432/barrelhealth?connect_timeout=5",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)


def initialize_database():
    schema = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
    with engine.begin() as conn:
        for statement in schema.split(";"):
            statement = statement.strip()
            if statement:
                conn.execute(text(statement))


def write_readings(df):
    columns = [
        "time",
        "machine_elapsed_seconds",
        "heater_elapsed_seconds",
        "zone",
        "temp_actual",
        "temp_set",
        "hdc",
        "source_health",
        "cause",
    ]
    df[columns].to_sql(
        "barrel_readings",
        engine,
        if_exists="append",
        index=False,
        method="multi",
    )


def load_readings():
    query = """
    SELECT time, machine_elapsed_seconds, heater_elapsed_seconds,
           zone, temp_actual, temp_set, hdc, source_health, cause
    FROM barrel_readings
    ORDER BY time, zone
"""
    return pd.read_sql(query, engine)


def write_predictions(df):
    columns = [
        "time",
        "zone",
        "actual_health",
        "predicted_health",
        "residual",
        "status",
    ]

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM health_predictions"))

    df[columns].to_sql(
        "health_predictions",
        engine,
        if_exists="append",
        index=False,
        method="multi",
    )