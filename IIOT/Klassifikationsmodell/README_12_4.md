## 12.4 Klassifikationsmodell für defekte Flaschen (20%)

### Ziel

Vorhersage, ob eine Flasche beim Vereinzeln beschädigt wurde (`is_cracked`,
0 = intakt, 1 = defekt), anhand der Vibrationsdaten beim Fall
(`drop_oscillation`, 500 Messwerte je Flasche als JSON-Array).

### Vorgehen

1. **Datenbasis:** Aus `bottles.csv` wurden alle Flaschen mit vollständigem
   `drop_oscillation`- und `is_cracked`-Wert verwendet: **488 Datensätze**,
   davon **41 defekt (≈ 8,4 %)** und 447 intakt. Die Klassen sind damit
   deutlich unbalanciert.

2. **Feature Engineering:** Da ein Modell nicht sinnvoll mit 500 rohen
   Zeitreihenwerten pro Flasche arbeiten kann, wurden daraus statistische
   Kennzahlen berechnet. Laut `1_Leistungsbewertung.md` sind dabei
   **RMS, Mean, STD, Min, Max, Range und Median** als Basis-Features
   gefordert; zusätzlich wurden eigene, ergänzende Merkmale getestet:
   - Pflicht: `RMS`, `Mean`, `STD`, `Min`, `Max`, `Range` (= ptp = max−min), `Median`
   - Ergänzend: Anzahl der Nulldurchgänge (grobes Frequenzmaß), Anzahl
     echter Peaks/Ausschläge (`scipy.signal.find_peaks`), Signalenergie
     (Summe der Quadrate), mittlerer Betrag

3. **Modelle:** Getestet wurden **kNN** (k-Nearest-Neighbors, k=7,
   distanzgewichtet) und **Logistische Regression** (mit
   `class_weight="balanced"` wegen der Klassenungleichheit), jeweils auf
   verschiedenen Feature-Kombinationen — darunter explizit auch die
   geforderte Pflicht-Feature-Kombination. Die Daten wurden vorab mit
   `StandardScaler` skaliert (wichtig v. a. für kNN, da es auf Distanzen
   zwischen Punkten basiert).

4. **Split:** 80 % Training / 20 % Test, stratifiziert nach `is_cracked`,
   damit auch im kleinen Testset genügend defekte Flaschen enthalten sind.

5. **Bewertung:** Wegen der starken Klassenungleichheit wäre reine
   Accuracy irreführend (ein Modell, das immer "intakt" vorhersagt, käme
   bereits auf ~91 % Accuracy). Daher wird stattdessen der **F1-Score**
   für die Klasse "defekt" sowie die **Confusion Matrix** herangezogen.

### Ergebnisse

| Genutzte Features | Modell-Typ | F1-Score (Training) | F1-Score (Test) |
|---|---|---|---|
| mean() | kNN | 1.000 | 0.333 |
| mean(), std() | kNN | 1.000 | 0.364 |
| mean(), std() | Log. Regression | 0.216 | 0.136 |
| RMS, Mean, STD, Min, Max, Range, Median (Pflicht-Features) | kNN | 1.000 | 0.222 |
| RMS, Mean, STD, Min, Max, Range, Median (Pflicht-Features) | Log. Regression | 0.214 | 0.145 |
| std(), ptp(), n_peaks() | **kNN (bestes Modell)** | 1.000 | **0.533** |
| std(), ptp(), n_peaks(), energy() | kNN | 1.000 | 0.533 |
| alle statist. Features (inkl. RMS, Median) | Log. Regression | 0.219 | 0.145 |
| alle statist. Features (inkl. RMS, Median) | kNN | 1.000 | 0.182 |

**Bestes Modell:** kNN (k=7, distanzgewichtet) mit den Features
`std()`, `ptp()` und `n_peaks()` — F1-Score (Test) = **0,533**.

> **Hinweis zum Trainings-F1 von 1.0:** Da kNN mit distanzbasierter
> Gewichtung arbeitet, ist ein Trainingspunkt bei der Vorhersage sein
> eigener nächster Nachbar mit (nahezu) unendlichem Gewicht — das Modell
> "lernt" die Trainingsdaten dadurch auswendig. Das ist ein bekanntes,
> normales Verhalten von kNN und kein Fehler. Die aussagekräftige Kennzahl
> ist der F1-Score auf den Testdaten.

### Confusion Matrix (bestes Modell, Testdaten)

![Confusion Matrix](confusion_matrix_best_model.png)

|              | Predicted: 0 (intakt) | Predicted: 1 (defekt) |
|--------------|:----------------------:|:-----------------------:|
| **Actual: 0** | 87 | 3 |
| **Actual: 1** | 4 | 4 |

### Interpretation

Von den 8 tatsächlich defekten Flaschen im Testset wurden 4 korrekt
erkannt (True Positives), 4 wurden übersehen (False Negatives). Nur 3
intakte Flaschen wurden fälschlich als defekt eingestuft (False
Positives). Angesichts von nur 41 defekten Flaschen in den gesamten
Trainingsdaten ist das ein akzeptables Ergebnis, zeigt aber auch die
Grenzen der Methode: Mit mehr Trainingsdaten (insbesondere mehr
defekten Flaschen) und feineren Merkmalen aus der Zeitreihe (z. B.
Frequenzanalyse per FFT) ließe sich die Erkennung vermutlich weiter
verbessern.

### Datei

Das vollständige Skript befindet sich in [`classification.py`](classification.py).
