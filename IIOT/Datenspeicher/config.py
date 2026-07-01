

MQTT_BROKER_HOST = "158.180.44.197"
MQTT_BROKER_PORT = 1883
MQTT_USERNAME = "bobm"
MQTT_PASSWORD = "letmein"


MQTT_BASE_TOPIC = "aut/SoSe26/learning_factory_simulation"
MQTT_SUBSCRIBE_TOPIC = f"{MQTT_BASE_TOPIC}/#"


TOPIC_RECIPE = "recipe"
TOPIC_DISPENSER_RED = "dispenser_red"
TOPIC_DISPENSER_BLUE = "dispenser_blue"
TOPIC_DISPENSER_GREEN = "dispenser_green"
TOPIC_TEMPERATURE = "temperature"
TOPIC_FINAL_WEIGHT = "scale/final_weight"
TOPIC_DROP_OSCILLATION = "drop_oscillation"
TOPIC_GROUND_TRUTH = "ground_truth"


DATA_DIR = "data"
BOTTLES_CSV = f"{DATA_DIR}/bottles.csv"
RECIPES_CSV = f"{DATA_DIR}/recipes.csv"
RAW_MESSAGES_CSV = f"{DATA_DIR}/raw_messages.csv"
PLOT_OUTPUT = f"{DATA_DIR}/plot_fill_levels.png"


RECONNECT_DELAY_MIN = 1
RECONNECT_DELAY_MAX = 30
