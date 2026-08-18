import matplotlib.pyplot as plt
import pandas as pd

from database import engine


def main():
    predictions = pd.read_sql(
        """
        SELECT time, zone, predicted_health
        FROM health_predictions
        ORDER BY time, zone
        """,
        engine,
    )

    if predictions.empty:
        print("No predictions found. Run: python main.py")
        return

    plt.figure(figsize=(12, 6))

    for zone, group in predictions.groupby("zone"):
        plt.plot(
            group["time"],
            group["predicted_health"],
            marker=".",
            label=f"Zone {zone}",
        )

    plt.xlabel("Time")
    plt.ylabel("Predicted Health (%)")
    plt.title("Barrel Health Trend")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("health_trend.png", dpi=300)

    print("Graph saved as health_trend.png")


if __name__ == "__main__":
    main()
