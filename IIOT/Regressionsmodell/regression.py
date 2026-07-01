import json

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

GRUPPE = "SimonUndDieStarkenMaenner"

BOTTLES_CSV = "bottles.csv"
X_CSV = "X.csv"
OUTPUT_CSV = f"reg_{GRUPPE}.csv"

RANDOM_STATE = 42
TEST_SIZE = 0.2


FEATURE_SETS = [
    # Kombinationen aus der Aufgabenstellung (Beispieltabelle):
    ["fill_level_grams_red"],
    ["fill_level_grams_red", "vibration_index_red"],
    ["fill_level_grams_red", "vibration_index_red", "temperature_red"],
    
    ["fill_level_grams_red", "fill_level_grams_blue", "fill_level_grams_green"],
    [
        "fill_level_grams_red", "fill_level_grams_blue", "fill_level_grams_green",
        "vibration_index_red", "vibration_index_blue", "vibration_index_green",
    ],
    [
        "fill_level_grams_red", "fill_level_grams_blue", "fill_level_grams_green",
        "vibration_index_red", "vibration_index_blue", "vibration_index_green",
        "temperature_red", "temperature_blue", "temperature_green",
    ],
]


def load_training_data() -> pd.DataFrame:
    
    df = pd.read_csv(BOTTLES_CSV)
    df = df.dropna(subset=["final_weight"])
    return df


def evaluate_feature_set(df: pd.DataFrame, features: list[str]) -> dict | None:
    """
    Trainiert ein lineares Modell auf den gegebenen Features und gibt
    Kennzahlen zurueck. Gibt None zurueck, falls eine Spalte fehlt.
    """
    missing = [f for f in features if f not in df.columns]
    if missing:
        return None

    data = df.dropna(subset=features + ["final_weight"])
    X = data[features].values
    y = data["final_weight"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)

    mse_train = mean_squared_error(y_train, y_train_pred)
    mse_test = mean_squared_error(y_test, y_test_pred)
    r2_train = r2_score(y_train, y_train_pred)
    r2_test = r2_score(y_test, y_test_pred)

    return {
        "features": features,
        "model": model,
        "mse_train": mse_train,
        "mse_test": mse_test,
        "r2_train": r2_train,
        "r2_test": r2_test,
        "n_samples": len(data),
    }


def format_formula(features: list[str], model: LinearRegression) -> str:
    """Formatiert die Modellformel als y = m1*x1 + m2*x2 + ... + b"""
    terms = [f"{coef:.4f}*{name}" for coef, name in zip(model.coef_, features)]
    return f"final_weight = {' + '.join(terms)} + {model.intercept_:.4f}"


def main():
    print("Lade Trainingsdaten aus bottles.csv ...")
    df = load_training_data()
    print(f"{len(df)} vollstaendige Flaschen-Datensaetze mit final_weight geladen.\n")

    results = []
    for features in FEATURE_SETS:
        result = evaluate_feature_set(df, features)
        if result is None:
            print(f"UEBERSPRUNGEN (Spalte fehlt in bottles.csv): {features}")
            continue
        results.append(result)
        print(f"Features: {features}")
        print(f"  n={result['n_samples']}, MSE Training={result['mse_train']:.4f}, "
              f"MSE Test={result['mse_test']:.4f}, R² Training={result['r2_train']:.4f}, "
              f"R² Test={result['r2_test']:.4f}")

    if not results:
        raise RuntimeError("Kein Feature-Set konnte ausgewertet werden!")

    
    best = min(results, key=lambda r: r["mse_test"])

    print("\n--- Bestes Modell ---")
    print(f"Features: {best['features']}")
    print(f"MSE Training: {best['mse_train']:.4f}")
    print(f"MSE Test:     {best['mse_test']:.4f}")
    print(format_formula(best["features"], best["model"]))

    #Vorhersage fuer X.csv mit dem besten Modell
    print(f"\nLade {X_CSV} fuer finale Vorhersage ...")
    X_new = pd.read_csv(X_CSV)

    missing_in_x = [f for f in best["features"] if f not in X_new.columns]
    if missing_in_x:
        raise RuntimeError(
            f"Bestes Modell braucht Spalten, die in {X_CSV} fehlen: {missing_in_x}"
        )

    y_hat = best["model"].predict(X_new[best["features"]].values)

    output = pd.DataFrame({
        "Flaschen_ID": X_new["bottle"],
        "y_hat": y_hat,
    })
    output.to_csv(OUTPUT_CSV, index=False)
    print(f"Vorhersage gespeichert unter: {OUTPUT_CSV}")
    print(output.head())

    return results, best


if __name__ == "__main__":
    main()
