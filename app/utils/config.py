import json
from pathlib import Path
from types import SimpleNamespace


def load_config(config_path):
    config_path = Path(config_path)

    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f, object_hook=lambda d: SimpleNamespace(**d))
