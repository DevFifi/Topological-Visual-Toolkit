import json
import os
from typing import Dict, Any

APP_STATE_PATH = os.path.join("data", "app_state.json")

DEFAULT_STATE: Dict[str, Any] = {
    "functions_1d": [],
    "functions_2d": [],
    "vector_mappings_r2_r2": [],
    "metrics": [],
    "custom_metrics": [],
    "points": [],
    "point_sets": [],
    "intervals": [],
    "rectangles": [],
    "sets_r": [],
    "sets_r2": [],
    "bernstein_examples": [],
    "viewports": [],
    "settings": {
        "precision_digits": 50,
        "grid_resolution_1d": 2000,
        "grid_resolution_2d": 250,
        "adaptive_refinement": True,
        "max_symbolic_n": 30,
    },
}

def ensure_data_dir_exists() -> None:
    data_dir = os.path.dirname(APP_STATE_PATH)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)

def load_state() -> Dict[str, Any]:
    ensure_data_dir_exists()
    if not os.path.exists(APP_STATE_PATH):
        return DEFAULT_STATE.copy()
    try:
        with open(APP_STATE_PATH, "r", encoding="utf-8") as f:
            state = json.load(f)
            for key, value in DEFAULT_STATE.items():
                if key not in state:
                    state[key] = value
            return state
    except (json.JSONDecodeError, IOError):
        return DEFAULT_STATE.copy()

def save_state(state: Dict[str, Any]) -> None:
    ensure_data_dir_exists()
    with open(APP_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
