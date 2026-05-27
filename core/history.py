import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from core.persistence import load_state, save_state

def _generate_id() -> str:
    return str(uuid.uuid4())

def _current_timestamp() -> str:
    return datetime.now().isoformat()

def get_history(category: str) -> List[Dict[str, Any]]:
    state = load_state()
    return state.get(category, [])

def add_or_update_history_entry(
    category: str,
    raw_value: str,
    label: str = "",
    parsed_preview: str = "",
    tags: Optional[List[str]] = None,
) -> None:
    state = load_state()
    if category not in state:
        state[category] = []
        
    entries = state[category]
    
    for entry in entries:
        if entry["raw_value"] == raw_value:
            entry["usage_count"] += 1
            entry["updated_at"] = _current_timestamp()
            if label:
                entry["label"] = label
            if parsed_preview:
                entry["parsed_preview"] = parsed_preview
            if tags:
                entry["tags"] = list(set(entry.get("tags", []) + tags))
            save_state(state)
            return

    new_entry = {
        "id": _generate_id(),
        "label": label,
        "raw_value": raw_value,
        "parsed_preview": parsed_preview,
        "category": category,
        "created_at": _current_timestamp(),
        "updated_at": _current_timestamp(),
        "usage_count": 1,
        "tags": tags or [],
    }
    entries.append(new_entry)
    save_state(state)

def remove_history_entry(category: str, entry_id: str) -> None:
    state = load_state()
    if category in state:
        state[category] = [e for e in state[category] if e.get("id") != entry_id]
        save_state(state)

def clear_history_category(category: str) -> None:
    state = load_state()
    if category in state:
        state[category] = []
        save_state(state)

def get_settings() -> Dict[str, Any]:
    state = load_state()
    return state.get("settings", {})

def update_settings(new_settings: Dict[str, Any]) -> None:
    state = load_state()
    if "settings" not in state:
        state["settings"] = {}
    state["settings"].update(new_settings)
    save_state(state)
