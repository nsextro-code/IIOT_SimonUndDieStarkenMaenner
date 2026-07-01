# Aufgabe 12.1.1 – MQTT-Client in TwinCAT

**Gruppe:** Simon und die starken Männer (Franz, Jäschke, Sextro)

## Vorgehen

Der Funktionsbaustein `FB_iot` verbindet sich über die Bibliothek
`Tc3_IotBase` (TF6701) mit dem Kurs-Broker und veröffentlicht periodisch
die Füllstände der drei Dispenser (rot, blau, grün) als MQTT-Nachrichten.

### Verbindungsaufbau

Beim ersten Zyklus (`first_cycle`) werden die Verbindungsdaten gesetzt:

| Parameter | Wert |
|---|---|
| Host | `158.180.44.197` |
| Port | `1883` |
| Topic-Prefix | `aut/SoSe26/SimonUndDieStarkenMaenner/` |
| Client-ID | `SimonUndDieStarkenMaenner-LF` |
| Benutzername / Passwort | `bobm` / `letmein` |

### Veröffentlichte Topics

**Einmalig beim Start (retained, mit `bQueue := TRUE`)**, getrennt von den
periodischen Messwerten über die Hilfsvariable `bStaticPublished`:

| Topic | Inhalt |
|---|---|
| `groupsname` | "Simon und die starken Männer" |
| `names` | Nachnamen der Gruppenmitglieder |
| `Fuellstand_rot$unit` / `_blau$unit` / `_gruen$unit` | jeweils `"g"` |

**Periodisch, alle 10 Sekunden** (`tmrSendMessageInterval`, retained):

| Topic | Inhalt |
|---|---|
| `Fuellstand_rot` | aktueller Füllstand Dispenser rot (`iUSS1`) |
| `Fuellstand_blau` | aktueller Füllstand Dispenser blau (`iUSS2`) |
| `Fuellstand_gruen` | aktueller Füllstand Dispenser grün (`iUSS3`) |

Alle Nachrichten werden mit `bRetain := TRUE` gesendet, damit auch ein
später hinzukommender Abonnent (z. B. der Dozent) sofort den letzten
bekannten Wert sieht, ohne auf den nächsten Sendezyklus warten zu müssen.

### Einbindung in MAIN

```
// Deklaration:
fbiot : FB_iot;

// Aufruf, am Ende des Programmzyklus:
fbiot(iUSS1 := iOut_USS1, iUSS2 := iOut_USS2, iUSS3 := iOut_USS3);
```

`iOut_USS1/2/3` sind die bereits im Projekt vorhandenen Füllstandwerte
(siehe `MAIN`-Deklaration), die von den `FB_System_Fullstand`-Instanzen
(`fbExt1/2/3`) berechnet werden.

## Bekannte Einschränkungen

- Deutsche Umlaute (ä, ö, ü) werden im MQTT-Payload nicht korrekt
  encodiert dargestellt. Dies ist ein bekanntes, noch ungelöstes Encoding-Problem von
  TwinCAT-Strings und beeinträchtigt nicht die Funktionalität.

## Testen / Verifizieren

1. TwinCAT-Projekt einloggen und starten (beide Instanzen: `LF_System_PLC`
   und `PLC`)
2. Anlage über die Visualisierung mit `Enable` und `Execute` starten
3. Mit MQTT Explorer (oder einem anderen MQTT-Client) auf
   `158.180.44.197:1883` verbinden (Benutzername `bobm`, Passwort
   `letmein`)
4. Unter dem Topic-Pfad `aut/SoSe26/SimonUndDieStarkenMaenner/` sollten
   die oben beschriebenen Werte ankommen und sich alle 10 Sekunden
   aktualisieren
