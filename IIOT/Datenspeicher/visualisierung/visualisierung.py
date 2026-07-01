

import time

import matplotlib.pyplot as plt
import pandas as pd

import config

REFRESH_INTERVAL_SECONDS = 10


def load_data() -> pd.DataFrame:
    try:
        df = pd.read_csv(config.BOTTLES_CSV)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame()
    return df


def plot_fill_levels(df: pd.DataFrame, ax) -> None:
    ax.clear()
    if df.empty:
        ax.set_title("Noch keine Daten vorhanden - warte auf erste Flasche...")
        return

    
    plot_df = df.copy()
    plot_df["time_red"] = pd.to_numeric(plot_df["time_red"], errors="coerce")
    plot_df = plot_df.sort_values("time_red")

    if "fill_level_grams_red" in plot_df:
        ax.plot(plot_df["time_red"], plot_df["fill_level_grams_red"],
                 color="red", marker="o", label="Rot")
    if "fill_level_grams_blue" in plot_df:
        ax.plot(plot_df["time_red"], plot_df["fill_level_grams_blue"],
                 color="blue", marker="o", label="Blau")
    if "fill_level_grams_green" in plot_df:
        ax.plot(plot_df["time_red"], plot_df["fill_level_grams_green"],
                 color="green", marker="o", label="Gruen")

    ax.set_xlabel("Zeit (Unix-Timestamp)")
    ax.set_ylabel("Fuellstand (Gramm)")
    ax.set_title(f"Fuellstaende der drei Dispenser ueber die Zeit "
                 f"({len(plot_df)} Flaschen)")
    ax.legend()
    ax.grid(True, alpha=0.3)


def run_live():
    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 6))

    print("Live-Plot gestartet. Aktualisiert sich automatisch. "
          "Fenster schliessen oder Strg+C zum Beenden.")

    try:
        while True:
            df = load_data()
            plot_fill_levels(df, ax)
            fig.canvas.draw()
            plt.pause(REFRESH_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("Beendet.")


def save_static_plot():
    
    df = load_data()
    fig, ax = plt.subplots(figsize=(10, 6))
    plot_fill_levels(df, ax)
    fig.savefig(config.PLOT_OUTPUT, dpi=120, bbox_inches="tight")
    print(f"Plot gespeichert unter: {config.PLOT_OUTPUT}")


if __name__ == "__main__":
    run_live()
