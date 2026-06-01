import json
import os
import shutil
from copy import deepcopy
from typing import Dict, Any

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_STATE_PATH = os.path.join(PROJECT_ROOT, "data", "app_state.json")
APP_STATE_DRAFT_PATH = os.path.join(PROJECT_ROOT, "data", "app_state_draft.json")
DRAFT_SEED_VERSION = 5
DRAFT_SEED_SETTING = "_draft_seed_version"

DEFAULT_STATE: Dict[str, Any] = {
    "functions_1d": [],
    "functions_2d": [],
    "supremum_interval_functions": [],
    "supremum_rectangle_functions": [],
    "bernstein_functions": [],
    "scalar_preimage_functions": [],
    "scalar_preimage_sets_r": [],
    "scalar_preimage_points": [],
    "vector_mapping_functions": [],
    "vector_mapping_sets_r2": [],
    "metric_points": [],
    "metric_params": [],
    "metric_custom_metrics": [],
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


def _default_state_copy() -> Dict[str, Any]:
    return deepcopy(DEFAULT_STATE)


def _read_json_file(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def _draft_path_candidates() -> list[str]:
    return [
        APP_STATE_DRAFT_PATH,
        os.path.join(PROJECT_ROOT, "data", "app_state_draft.json"),
        os.path.join(os.getcwd(), "data", "app_state_draft.json"),
    ]


def _find_existing_draft_path() -> str | None:
    seen = set()
    for path in _draft_path_candidates():
        normalized = os.path.abspath(path)
        if normalized in seen:
            continue
        seen.add(normalized)
        if os.path.exists(normalized):
            return normalized
    return None


def _load_draft_state() -> Dict[str, Any]:
    draft_path = _find_existing_draft_path()
    if draft_path is None:
        return _default_state_copy()
    try:
        draft = _read_json_file(draft_path)
    except (json.JSONDecodeError, IOError):
        return _default_state_copy()
    return _ensure_default_keys(draft)


def _ensure_default_keys(state: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in DEFAULT_STATE.items():
        if key not in state:
            state[key] = deepcopy(value)

    settings = state.get("settings")
    if not isinstance(settings, dict):
        state["settings"] = deepcopy(DEFAULT_STATE["settings"])
    else:
        merged_settings = deepcopy(DEFAULT_STATE["settings"])
        merged_settings.update(settings)
        state["settings"] = merged_settings
    return state


def _draft_seed_version(state: Dict[str, Any]) -> int:
    settings = state.get("settings")
    if not isinstance(settings, dict):
        return 0
    version = settings.get(DRAFT_SEED_SETTING, 0)
    return version if isinstance(version, int) else 0


def _mark_draft_seeded(state: Dict[str, Any]) -> Dict[str, Any]:
    settings = state.get("settings")
    if not isinstance(settings, dict):
        settings = {}
    settings[DRAFT_SEED_SETTING] = DRAFT_SEED_VERSION
    state["settings"] = settings
    return state


def _merge_draft_examples(state: Dict[str, Any]) -> Dict[str, Any]:
    draft = _load_draft_state()
    state = _ensure_default_keys(state)

    for key, draft_value in draft.items():
        if key == "settings" and isinstance(draft_value, dict):
            settings = dict(draft_value)
            settings.update(state.get("settings", {}))
            state["settings"] = settings
            continue
        if not isinstance(draft_value, list):
            continue

        current_value = state.get(key, [])
        if not isinstance(current_value, list):
            current_value = []

        merged = list(current_value)
        existing_by_id = {
            entry.get("id"): idx
            for idx, entry in enumerate(merged)
            if isinstance(entry, dict) and entry.get("id")
        }
        existing_raw = {entry.get("raw_value") for entry in merged if isinstance(entry, dict)}
        for entry in draft_value:
            if not isinstance(entry, dict):
                continue
            entry_id = entry.get("id")
            if entry_id in existing_by_id:
                merged[existing_by_id[entry_id]] = entry
                existing_raw.add(entry.get("raw_value"))
                continue
            if entry.get("raw_value") in existing_raw:
                continue
            merged.append(entry)
            if entry_id:
                existing_by_id[entry_id] = len(merged) - 1
            existing_raw.add(entry.get("raw_value"))
        state[key] = merged
    return state


def load_state() -> Dict[str, Any]:
    ensure_data_dir_exists()
    if not os.path.exists(APP_STATE_PATH):
        state = _load_draft_state()
        _mark_draft_seeded(state)
        save_state(state)
        return state
    try:
        state = _read_json_file(APP_STATE_PATH)
        if _draft_seed_version(state) < DRAFT_SEED_VERSION:
            state = _merge_draft_examples(state)
            _mark_draft_seeded(state)
            save_state(state)
            return state
        return _ensure_default_keys(state)
    except (json.JSONDecodeError, IOError):
        state = _load_draft_state()
        _mark_draft_seeded(state)
        save_state(state)
        return state

def save_state(state: Dict[str, Any]) -> None:
    ensure_data_dir_exists()
    with open(APP_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def reset_state_from_draft() -> None:
    ensure_data_dir_exists()
    draft_path = _find_existing_draft_path()
    if draft_path is None:
        searched = ", ".join(os.path.abspath(path) for path in _draft_path_candidates())
        raise FileNotFoundError(f"Nie znaleziono app_state_draft.json. Sprawdzone ścieżki: {searched}")
    _read_json_file(draft_path)
    shutil.copyfile(draft_path, APP_STATE_PATH)
