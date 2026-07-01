import json
import signal
import sys

import paho.mqtt.client as mqtt

import config
from database import database
from database.transform import BottleStore

store = BottleStore()


def _topic_suffix(full_topic: str) -> str:
    
    prefix = config.MQTT_BASE_TOPIC + "/"
    if full_topic.startswith(prefix):
        return full_topic[len(prefix):]
    return full_topic


def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        print(f"Verbunden mit Broker {config.MQTT_BROKER_HOST}:{config.MQTT_BROKER_PORT}")
        client.subscribe(config.MQTT_SUBSCRIBE_TOPIC, qos=config.MQTT_QOS)
        print(f"Abonniert: {config.MQTT_SUBSCRIBE_TOPIC}")
    else:
        print(f"Verbindung fehlgeschlagen, Code: {reason_code}")


def on_disconnect(client, userdata, flags, reason_code, properties=None):
    print(f"Verbindung zum Broker getrennt (Code {reason_code}). Versuche erneut zu verbinden...")


def on_message(client, userdata, message):
    topic = message.topic
    payload_raw = message.payload.decode(errors="replace")

    
    try:
        database.append_raw_message(topic, payload_raw)
    except Exception as e:
        print(f"Konnte raw_message nicht schreiben: {e}")

    
    try:
        payload = json.loads(payload_raw)
    except (json.JSONDecodeError, ValueError):
        print(f"Ungueltiges JSON auf Topic '{topic}', wird uebersprungen: {payload_raw[:80]}")
        return

    suffix = _topic_suffix(topic)

    try:
        if suffix == config.TOPIC_RECIPE:
            database.append_recipe(payload)

        elif suffix == config.TOPIC_DISPENSER_RED:
            store.handle_dispenser("red", payload)

        elif suffix == config.TOPIC_DISPENSER_BLUE:
            store.handle_dispenser("blue", payload)

        elif suffix == config.TOPIC_DISPENSER_GREEN:
            store.handle_dispenser("green", payload)

        elif suffix == config.TOPIC_TEMPERATURE:
            
            store.handle_temperature(payload)

        elif suffix == config.TOPIC_FINAL_WEIGHT:
            store.handle_final_weight(payload)

        elif suffix == config.TOPIC_DROP_OSCILLATION:
            store.handle_drop_oscillation(payload)

        elif suffix == config.TOPIC_GROUND_TRUTH:
            finished_bottle = store.handle_ground_truth(payload)
            if finished_bottle is not None:
                database.append_bottle(finished_bottle)
                print(f"Flasche {finished_bottle.bottle} komplett gespeichert "
                      f"(is_cracked={finished_bottle.is_cracked})")

        else:
            print(f"Unbekanntes Topic '{suffix}', nur roh geloggt.")

    except KeyError as e:
        print(f"Erwartetes Feld fehlt in Nachricht auf '{topic}': {e}")
    except Exception as e:
        print(f"Fehler bei der Verarbeitung von '{topic}': {e}")


def _save_open_bottles_and_exit(signum, frame):
    print("\nBeende... speichere noch offene (unvollstaendige) Flaschen-Datensaetze.")
    remaining = store.pop_all_open()
    for bottle in remaining:
        database.append_bottle(bottle)
    print(f"{len(remaining)} unvollstaendige Flasche(n) zusaetzlich gespeichert.")
    sys.exit(0)


def main():
    database.ensure_data_dir()

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    
    client.reconnect_delay_set(min_delay=config.RECONNECT_DELAY_MIN,
                                max_delay=config.RECONNECT_DELAY_MAX)

    signal.signal(signal.SIGINT, _save_open_bottles_and_exit)

    print(f"Verbinde mit {config.MQTT_BROKER_HOST}:{config.MQTT_BROKER_PORT} ...")
    client.connect(config.MQTT_BROKER_HOST, config.MQTT_BROKER_PORT)

    print("Warte auf Nachrichten. Zum Beenden Strg+C druecken.")
    client.loop_forever()


if __name__ == "__main__":
    main()
