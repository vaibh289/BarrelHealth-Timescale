CREATE TABLE IF NOT EXISTS barrel_readings (
    time TIMESTAMPTZ NOT NULL,
    machine_elapsed_seconds DOUBLE PRECISION,
    heater_elapsed_seconds DOUBLE PRECISION,
    zone TEXT NOT NULL,
    temp_actual DOUBLE PRECISION,
    temp_set DOUBLE PRECISION,
    hdc DOUBLE PRECISION,
    source_health DOUBLE PRECISION,
    cause TEXT
);

SELECT create_hypertable(
    'barrel_readings',
    by_range('time'),
    if_not_exists => TRUE
);

CREATE INDEX IF NOT EXISTS barrel_readings_zone_time_idx
ON barrel_readings (zone, time DESC);

CREATE TABLE IF NOT EXISTS health_predictions (
    time TIMESTAMPTZ NOT NULL,
    zone TEXT NOT NULL,
    actual_health DOUBLE PRECISION,
    predicted_health DOUBLE PRECISION,
    residual DOUBLE PRECISION,
    status TEXT NOT NULL
);

SELECT create_hypertable(
    'health_predictions',
    by_range('time'),
    if_not_exists => TRUE
);

CREATE INDEX IF NOT EXISTS health_predictions_zone_time_idx
ON health_predictions (zone, time DESC);
