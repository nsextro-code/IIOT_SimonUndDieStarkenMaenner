import json

import numpy as np
import pandas as pd
from scipy.signal import find_peaks
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay

GRUPPE = "SimonUndDieStarkenMaenner"

BOTTLES_CSV = "bottles.csv"
CONFUSION_MATRIX_PNG = "confusion_matrix_best_model.png"

RANDOM_STATE = 42
TEST_SIZE = 0.2


def load_data() -> pd.DataFrame:
    
    df = pd.read_csv(BOTTLES_CSV)
    df = df.dropna(subset=["drop_oscillation", "is_cracked"])
    df["is_cracked"] = df["is_cracked"].astype(int)
    return df


def extract_oscillation_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Wandelt die drop_oscillation-JSON-Strings (500 Messwerte je Flasche)
    in statistische Features um. Enthaelt insbesondere die laut
    1_Leistungsbewertung.md geforderten Kennzahlen:
    RMS, Mean, STD, Min, Max, Range, Median.
    Zusaetzlich: Nulldurchgaenge, Anzahl echter Peaks und Signalenergie
    als eigene, ergaenzende Merkmale.
    """
    means, stds, mins, maxs, ptps, medians, rms_vals = [], [], [], [], [], [], []
    zero_crossings, n_peaks, energy, abs_mean = [], [], [], []

    for raw in df["drop_oscillation"]:
        values = np.array(json.loads(raw), dtype=float)
        means.append(values.mean())
        stds.append(values.std())
        mins.append(values.min())
        maxs.append(values.max())
        ptps.append(values.max() - values.min())          # Range
        medians.append(float(np.median(values)))          # Median
        rms_vals.append(float(np.sqrt(np.mean(values ** 2))))  # RMS
        signs = np.sign(values)
        zero_crossings.append(int(np.sum(np.diff(signs) != 0)))
        peaks, _ = find_peaks(np.abs(values), height=values.std())
        n_peaks.append(len(peaks))
        energy.append(float(np.sum(values ** 2)))
        abs_mean.append(float(np.mean(np.abs(values))))

    df = df.copy()
    df["osc_mean"] = means
    df["osc_std"] = stds
    df["osc_min"] = mins
    df["osc_max"] = maxs
    df["osc_ptp"] = ptps          # Range
    df["osc_median"] = medians
    df["osc_rms"] = rms_vals
    df["osc_zero_crossings"] = zero_crossings
    df["osc_n_peaks"] = n_peaks
    df["osc_energy"] = energy
    df["osc_abs_mean"] = abs_mean
    return df



EXPERIMENTS = [
    {"name": "mean()", "features": ["osc_mean"], "model": "knn"},
    {"name": "mean(), std()", "features": ["osc_mean", "osc_std"], "model": "knn"},
    {"name": "mean(), std()", "features": ["osc_mean", "osc_std"], "model": "logreg"},
    {
        "name": "RMS, Mean, STD, Min, Max, Range, Median (Pflicht-Features)",
        "features": [
            "osc_rms", "osc_mean", "osc_std", "osc_min",
            "osc_max", "osc_ptp", "osc_median",
        ],
        "model": "knn",
    },
    {
        "name": "RMS, Mean, STD, Min, Max, Range, Median (Pflicht-Features)",
        "features": [
            "osc_rms", "osc_mean", "osc_std", "osc_min",
            "osc_max", "osc_ptp", "osc_median",
        ],
        "model": "logreg",
    },
    {
        "name": "std(), ptp(), n_peaks()",
        "features": ["osc_std", "osc_ptp", "osc_n_peaks"],
        "model": "knn",
    },
    {
        "name": "std(), ptp(), n_peaks(), energy()",
        "features": ["osc_std", "osc_ptp", "osc_n_peaks", "osc_energy"],
        "model": "knn",
    },
    {
        "name": "alle statist. Features (RMS, mean, std, min, max, ptp, "
                "median, zero_crossings, n_peaks, energy, abs_mean)",
        "features": [
            "osc_rms", "osc_mean", "osc_std", "osc_min", "osc_max", "osc_ptp",
            "osc_median", "osc_zero_crossings", "osc_n_peaks", "osc_energy",
            "osc_abs_mean",
        ],
        "model": "logreg",
    },
    {
        "name": "alle statist. Features (RMS, mean, std, min, max, ptp, "
                "median, zero_crossings, n_peaks, energy, abs_mean)",
        "features": [
            "osc_rms", "osc_mean", "osc_std", "osc_min", "osc_max", "osc_ptp",
            "osc_median", "osc_zero_crossings", "osc_n_peaks", "osc_energy",
            "osc_abs_mean",
        ],
        "model": "knn",
    },
]


def build_model(kind: str):
    if kind == "knn":
        return KNeighborsClassifier(n_neighbors=7, weights="distance")
    if kind == "logreg":
        return LogisticRegression(max_iter=1000, class_weight="balanced")
    raise ValueError(f"Unbekannter Modelltyp: {kind}")


def run_experiment(df: pd.DataFrame, features: list[str], model_kind: str) -> dict:
    X = df[features].values
    y = df["is_cracked"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    # Skalierung ist v.a. fuer kNN wichtig (Distanzmass), schadet
    # bei Logistischer Regression aber nicht.
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    model = build_model(model_kind)
    model.fit(X_train_s, y_train)

    y_train_pred = model.predict(X_train_s)
    y_test_pred = model.predict(X_test_s)

    f1_train = f1_score(y_train, y_train_pred, zero_division=0)
    f1_test = f1_score(y_test, y_test_pred, zero_division=0)
    cm_test = confusion_matrix(y_test, y_test_pred, labels=[0, 1])

    return {
        "features": features,
        "model_kind": model_kind,
        "model": model,
        "scaler": scaler,
        "f1_train": f1_train,
        "f1_test": f1_test,
        "cm_test": cm_test,
        "y_test": y_test,
        "y_test_pred": y_test_pred,
    }


def main():
    print("Lade Trainingsdaten aus bottles.csv ...")
    df = load_data()
    print(f"{len(df)} Flaschen-Datensaetze mit drop_oscillation und is_cracked geladen.")
    print(f"Klassenverteilung: {df['is_cracked'].value_counts().to_dict()}\n")

    df = extract_oscillation_features(df)

    results = []
    for exp in EXPERIMENTS:
        result = run_experiment(df, exp["features"], exp["model"])
        result["name"] = exp["name"]
        results.append(result)
        print(f"[{exp['model']:6s}] {exp['name']:40s} "
              f"F1 Training={result['f1_train']:.3f}  F1 Test={result['f1_test']:.3f}")

    # Bestes Modell nach F1-Score auf dem Testset
    best = max(results, key=lambda r: r["f1_test"])
    print("\n--- Bestes Modell ---")
    print(f"Features: {best['features']}")
    print(f"Modell: {best['model_kind']}")
    print(f"F1 Training: {best['f1_train']:.3f}")
    print(f"F1 Test:     {best['f1_test']:.3f}")
    print("Confusion Matrix (Test):")
    print(best["cm_test"])

    # Confusion-Matrix-Plot fuer README
    disp = ConfusionMatrixDisplay(
        confusion_matrix=best["cm_test"], display_labels=["intakt (0)", "defekt (1)"]
    )
    disp.plot(cmap="Blues", values_format="d")
    plt.title(f"Confusion Matrix – bestes Modell ({best['model_kind']}, {best['name']})")
    plt.tight_layout()
    plt.savefig(CONFUSION_MATRIX_PNG, dpi=150)
    print(f"\nConfusion-Matrix-Plot gespeichert unter: {CONFUSION_MATRIX_PNG}")

    # F1-Tabelle als Markdown fuer das README generieren
    print("\n--- F1-Tabelle (Markdown fuer README) ---\n")
    print("| Genutzte Features | Modell-Typ | F1-Score (Training) | F1-Score (Test) |")
    print("|---|---|---|---|")
    model_label = {"knn": "kNN", "logreg": "Log. Regression"}
    for r in results:
        marker = " **(beste)**" if r is best else ""
        print(f"| {r['name']} | {model_label[r['model_kind']]}{marker} "
              f"| {r['f1_train']:.3f} | {r['f1_test']:.3f} |")

    return results, best


if __name__ == "__main__":
    main()
