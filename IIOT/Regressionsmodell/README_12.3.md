# Aufgabe 12.3 – Regressionsmodell für Endgewicht

**Gruppe:** Simon und die starken Männer (Franz, Jäschke, Sextro)

## Vorgehen

Trainiert wird auf den in Aufgabe 12.1.2 gesammelten Daten (`bottles.csv`,
490 Flaschen, davon 488 mit vollständigem `final_weight`). Die restlichen 2
Zeilen (Flaschen, die beim Beenden des MQTT-Clients noch nicht fertig
durchgelaufen waren) wurden entfernt.

Für jede Spaltenkombination wurde:
1. Ein 80/20-Split in Trainings- und Testdaten durchgeführt
   (`train_test_split`, `random_state=42`)
2. Ein lineares Regressionsmodell (`sklearn.linear_model.LinearRegression`)
   trainiert
3. Der MSE (Mean Squared Error) sowohl auf den Trainings- als auch auf den
   Testdaten berechnet

## Ergebnisse

| Genutzte Spalten (`x`) | Modell-Typ | MSE (Training) | MSE (Test) | R² (Training) | R² (Test) |
|---|---|---|---|---|---|
| `fill_level_grams_red` | Linear | 30.79 | 27.35 | 0.13 | 0.21 |
| `fill_level_grams_red`, `vibration_index_red` | Linear | 3.72 | 2.60 | 0.90 | 0.92 |
| `fill_level_grams_red`, `vibration_index_red`, `temperature_red` | Linear | 3.97 | 1.58 | 0.89 | 0.95 |
| `fill_level_grams_red`, `fill_level_grams_blue`, `fill_level_grams_green` | Linear | 29.34 | 25.69 | 0.17 | 0.26 |
| **`fill_level_grams_red`, `fill_level_grams_blue`, `fill_level_grams_green`, `vibration_index_red`, `vibration_index_blue`, `vibration_index_green`** | **Linear** | **0.1104** | **0.1027** | **0.997** | **0.997** |
| `fill_level_grams_red`, `fill_level_grams_blue`, `fill_level_grams_green`, `vibration_index_red`, `vibration_index_blue`, `vibration_index_green`, `temperature_red`, `temperature_blue`, `temperature_green` | Linear | 0.1106 | 0.1044 | 0.997 | 0.997 |

## Bestes Modell

Die Kombination aller drei Füllstände und aller drei Vibrationsindizes
liefert mit deutlichem Abstand den niedrigsten Fehler (MSE Test = 0.1027,
R² Test = 0.997 – das Modell erklärt also 99,7 % der Varianz im
Endgewicht). Das Hinzufügen der Temperatur verbessert das Ergebnis nicht
weiter (MSE Test steigt leicht auf 0.1044) – die Füllstände und
Vibrationsindizes allein erklären das Endgewicht bereits nahezu
vollständig.

**Formel des besten Modells** (`y = mx + b`, hier mit mehreren `x`):

```
final_weight =
    0.0005 * fill_level_grams_red
  + 0.0004 * fill_level_grams_blue
  + 0.0006 * fill_level_grams_green
  + 0.0997 * vibration_index_red
  + 0.0762 * vibration_index_blue
  + 0.1001 * vibration_index_green
  - 3.4332
```

## Vorhersage für X.csv

Mit diesem besten Modell wurde die Vorhersage für den gemeinsamen
Prognose-Datensatz `X.csv` (247 Flaschen, ohne `final_weight`) erstellt und
in `reg_SimonUndDieStarkenMaenner.csv` gespeichert:

| Flaschen_ID | y_hat |
|---|---|
| 368 | 43.19 |
| 369 | 41.01 |
| 370 | 41.47 |
| 371 | 18.17 |
| 372 | 17.15 |

## Setup & Ausführung

```bash
pip install -r requirements.txt
python regression.py
```

Voraussetzung: `bottles.csv` (aus 12.1.2) und `X.csv` (vom Kurs
bereitgestellt) liegen im selben Ordner wie `regression.py`.
