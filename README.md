# BarrelHealth-Timescale

A fresh BarrelHealth project using TimescaleDB/PostgreSQL for time-series storage.

## 1. Add your data

Copy your original `data.tsv` into:

`data/data.tsv`

Expected columns:

`machine_time,heater_time,zone,temp_actual,temp_set,hdc,health,cause`

## 2. Start TimescaleDB

Install Docker Desktop, then from this project folder run:

`docker compose up -d`

## 3. Create the Python environment

PowerShell:

`python -m venv venv`

`.env\Scripts\Activate.ps1`

Install packages:

`pip install -r requirements.txt`

## 4. Import the data

`python import_data.py`

## 5. Run the health/ML pipeline

`python main.py`

## 6. Create the graph

`python dashboard.py`

The graph is saved as `health_trend.png`.

Default database:

`postgresql+psycopg://barreluser:barrelpass@localhost:5432/barrelhealth`

## Important ML note

Your current `health` value is calculated directly from temperature error. Therefore the Random Forest is learning a relationship already encoded by the health formula. A later version should predict future health/failure from historical readings if the goal is genuine predictive maintenance.
