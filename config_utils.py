import json, os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

def read_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)
