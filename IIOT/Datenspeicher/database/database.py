import csv
import os
import time

from database.transform import BottleRecord
import config


def ensure_data_dir() -> None:
    os.makedirs(config.DATA_DIR, exist_ok=True)


def _write_header_if_new(path: str, fieldnames: list[str]) -> None:
    
    file_is_new = not os.path.exists(path) or os.path.getsize(path) == 0
    if file_is_new:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()


def append_bottle(record: BottleRecord) -> None:
    
    ensure_data_dir()
    fieldnames = BottleRecord.csv_fieldnames()
    _write_header_if_new(config.BOTTLES_CSV, fieldnames)
    with open(config.BOTTLES_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow(record.to_csv_row())


def append_recipe(payload: dict) -> None:
    
    ensure_data_dir()
    fieldnames = ["id", "creation_date", "color_levels_grams", "received_at"]
    _write_header_if_new(config.RECIPES_CSV, fieldnames)
    row = {
        "id": payload.get("id"),
        "creation_date": payload.get("creation_date"),
        
        "color_levels_grams": payload.get("color_levels_grams"),
        "received_at": time.time(),
    }
    with open(config.RECIPES_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow(row)


def append_raw_message(topic: str, payload_raw: str) -> None:
    
    ensure_data_dir()
    fieldnames = ["received_at", "topic", "payload"]
    _write_header_if_new(config.RAW_MESSAGES_CSV, fieldnames)
    row = {
        "received_at": time.time(),
        "topic": topic,
        "payload": payload_raw,
    }
    with open(config.RAW_MESSAGES_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow(row)
