# Aufgabe 12.1.2 – Datenspeicherung & Visualisierung

**Gruppe:** Simon und die starken Männer (Franz, Jäschke, Sextro)

## Beschreibung

Dieses Python-Programm verbindet sich mit dem Kurs-MQTT-Broker und empfängt
den Datenstrom der Learning Factory Simulation. Die eingehenden Nachrichten
werden pro Flasche zusammengeführt, in einer CSV-Datei gespeichert und live
als Diagramm visualisiert.

## Was das Programm macht

- Verbindet sich automatisch mit dem Broker (`158.180.44.197:1883`) und
  abonniert alle relevanten Topics der Simulation
- Alle eingehenden Nachrichten werden einem Sicherheitsnetz-Log
  (`raw_messages.csv`) gespeichert
- Pro Flasche werden die Daten aller Topics (Füllstand, Vibration,
  Temperatur, Endgewicht, Schwingung beim Fall, Qualitätslabel) zu
  **einer Zeile** zusammengeführt und in `bottles.csv` gespeichert
- Ein Live-Plot zeigt die Füllstände aller drei Dispenser über die Zeit
  und **aktualisiert sich automatisch**, während neue Daten hereinkommen

## Datenstruktur `bottles.csv`

| Spalte | Bedeutung |
|---|---|
| `bottle` | Flaschen-ID (String) |
| `recipe` | Rezept-ID dieser Flasche |
| `time_red/blue/green` | Zeitstempel je Dispenser |
| `fill_level_grams_red/blue/green` | Füllstand je Farbe in Gramm |
| `vibration_index_red/blue/green` | Vibrationsindex je Dispenser |
| `temperature_red/blue/green` | Temperatur je Dispenser in °C |
| `time_final_weight`, `final_weight` | Zeitpunkt & Gewicht der Waage |
| `drop_oscillation` | Liste mit 500 Schwingungswerten als JSON-String |
| `is_cracked` | "0"/"1" – ob die Flasche beim Fall gesprungen ist |

## Setup & Ausführung

```bash
pip install -r requirements.txt

# 1. Daten sammeln (mindestens 15 Minuten, dann Strg+C zum Beenden)
python -m mqtt_client.mqtt_client

# 2. Live-Plot anzeigen (in einem zweiten Terminal, während Schritt 1 läuft)
python -m visualisierung.visualisierung
```

Die gesamte Konfiguration (Broker-Adresse, Zugangsdaten, Dateipfade) liegt
zentral in `config.py` und kann dort einfach angepasst werden.

## Ergebnis

Nach mindestens 15 Minuten Datensammlung sind alle relevanten Daten in
`data/bottles.csv` gespeichert. Der folgende Plot zeigt die Füllstände
aller drei Dispenser über die Zeit – rot, blau und grün entsprechen den
drei Abfüllstationen:

![Füllstand-Plot](data/plot_fill_levels.png)

Das typische Sägezahn-Muster zeigt, wie jeder Tank kontinuierlich für viele
Flaschen genutzt wird (Füllstand sinkt), bis er leer ist und automatisch
wieder nachgefüllt wird (steiler Sprung nach oben).

## Fehlerbehandlung

- Bei Verbindungsabbruch zum Broker wird automatisch erneut verbunden
- Ungültige Nachrichten werden übersprungen, ohne das Programm zu beenden
- Beim Beenden (Strg+C) werden noch offene, unvollständige
  Flaschen-Datensätze ebenfalls gespeichert und nicht verworfen
