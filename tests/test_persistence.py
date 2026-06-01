import shutil
import tempfile
from pathlib import Path

from core import persistence


def test_reset_state_from_draft_copies_draft_exactly(monkeypatch):
    temp_dir = Path(tempfile.mkdtemp(prefix="persistence-test-", dir=Path.cwd()))
    try:
        app_state = temp_dir / "app_state.json"
        draft_state = temp_dir / "app_state_draft.json"
        draft_text = '{"settings":{"_draft_seed_version":99},"metric_points":[{"id":"x","raw_value":"line(count=1000, dim=50)"}]}'
        app_state.write_text('{"settings":{"_draft_seed_version":1},"metric_points":[]}', encoding="utf-8")
        draft_state.write_text(draft_text, encoding="utf-8")

        monkeypatch.setattr(persistence, "APP_STATE_PATH", str(app_state))
        monkeypatch.setattr(persistence, "APP_STATE_DRAFT_PATH", str(draft_state))

        persistence.reset_state_from_draft()

        assert app_state.read_text(encoding="utf-8") == draft_text
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_reset_state_from_draft_missing_draft_does_not_clear_app_state(monkeypatch):
    temp_dir = Path(tempfile.mkdtemp(prefix="persistence-test-", dir=Path.cwd()))
    try:
        app_state = temp_dir / "app_state.json"
        draft_state = temp_dir / "missing_draft.json"
        original_text = '{"settings":{"_draft_seed_version":1},"metric_points":[{"id":"old"}]}'
        app_state.write_text(original_text, encoding="utf-8")

        monkeypatch.setattr(persistence, "APP_STATE_PATH", str(app_state))
        monkeypatch.setattr(persistence, "APP_STATE_DRAFT_PATH", str(draft_state))
        monkeypatch.setattr(persistence, "PROJECT_ROOT", str(temp_dir))
        monkeypatch.chdir(temp_dir)

        try:
            persistence.reset_state_from_draft()
        except FileNotFoundError:
            pass
        else:
            raise AssertionError("reset_state_from_draft should fail when draft is missing")

        assert app_state.read_text(encoding="utf-8") == original_text
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_reset_state_from_draft_accepts_utf8_bom(monkeypatch):
    temp_dir = Path(tempfile.mkdtemp(prefix="persistence-test-", dir=Path.cwd()))
    try:
        app_state = temp_dir / "app_state.json"
        draft_state = temp_dir / "app_state_draft.json"
        draft_text = '{"settings":{"_draft_seed_version":99},"metric_points":[{"id":"x"}]}'
        app_state.write_text('{"settings":{}}', encoding="utf-8")
        draft_state.write_text("\ufeff" + draft_text, encoding="utf-8")

        monkeypatch.setattr(persistence, "APP_STATE_PATH", str(app_state))
        monkeypatch.setattr(persistence, "APP_STATE_DRAFT_PATH", str(draft_state))
        monkeypatch.setattr(persistence, "PROJECT_ROOT", str(temp_dir))

        persistence.reset_state_from_draft()
        loaded = persistence._read_json_file(str(app_state))

        assert loaded["metric_points"][0]["id"] == "x"
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
