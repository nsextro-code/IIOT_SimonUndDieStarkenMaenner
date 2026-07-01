
import json
from dataclasses import dataclass, field, fields
from typing import Optional


@dataclass
class BottleRecord:
    
    bottle: str
    recipe: Optional[str] = None

    # Dispenser rot
    time_red: Optional[str] = None
    fill_level_grams_red: Optional[float] = None
    vibration_index_red: Optional[float] = None
    temperature_red: Optional[float] = None

    # Dispenser blau
    time_blue: Optional[str] = None
    fill_level_grams_blue: Optional[float] = None
    vibration_index_blue: Optional[float] = None
    temperature_blue: Optional[float] = None

    # Dispenser gruen
    time_green: Optional[str] = None
    fill_level_grams_green: Optional[float] = None
    vibration_index_green: Optional[float] = None
    temperature_green: Optional[float] = None

    # Waage
    time_final_weight: Optional[str] = None
    final_weight: Optional[float] = None

    # Vereinzelung / Schwingung
    drop_oscillation: Optional[str] = None  
    # Ground Truth
    is_cracked: Optional[str] = None  
    
    complete: bool = False

    @staticmethod
    def csv_fieldnames():
        
        return [f.name for f in fields(BottleRecord) if f.name != "complete"]

    def to_csv_row(self) -> dict:
        row = {}
        for f in fields(self):
            if f.name == "complete":
                continue
            row[f.name] = getattr(self, f.name)
        return row


class BottleStore:
    

    def __init__(self):
        self._bottles: dict[str, BottleRecord] = {}
        
        self._last_temperature: dict[str, float] = {"red": None, "blue": None, "green": None}

    def handle_temperature(self, payload: dict) -> None:
        
        color = payload.get("dispenser")
        if color in self._last_temperature:
            self._last_temperature[color] = payload.get("temperature_C")

    def _get_or_create(self, bottle_id: str) -> BottleRecord:
        bottle_id = str(bottle_id)
        if bottle_id not in self._bottles:
            self._bottles[bottle_id] = BottleRecord(bottle=bottle_id)
        return self._bottles[bottle_id]

    def handle_dispenser(self, color: str, payload: dict) -> None:
        """color ist 'red', 'blue' oder 'green'."""
        bottle = self._get_or_create(payload["bottle"])
        setattr(bottle, f"time_{color}", payload.get("time"))
        setattr(bottle, f"fill_level_grams_{color}", payload.get("fill_level_grams"))
        
        setattr(bottle, f"vibration_index_{color}", payload.get("vibration-index"))
        
        setattr(bottle, f"temperature_{color}", self._last_temperature.get(color))
        
        if bottle.recipe is None and "recipe" in payload:
            bottle.recipe = str(payload["recipe"])

    def handle_final_weight(self, payload: dict) -> None:
        bottle = self._get_or_create(payload["bottle"])
        bottle.time_final_weight = payload.get("time")
        bottle.final_weight = payload.get("final_weight")

    def handle_drop_oscillation(self, payload: dict) -> None:
        bottle = self._get_or_create(payload["bottle"])
        
        bottle.drop_oscillation = json.dumps(payload.get("drop_oscillation"))

    def handle_ground_truth(self, payload: dict) -> Optional[BottleRecord]:

        bottle_id = str(payload["bottle"])
        bottle = self._get_or_create(bottle_id)
        
        bottle.is_cracked = str(payload.get("is_cracked"))
        bottle.complete = True

        finished = self._bottles.pop(bottle_id)
        return finished

    def pop_all_open(self) -> list[BottleRecord]:
        
        remaining = list(self._bottles.values())
        self._bottles.clear()
        return remaining
