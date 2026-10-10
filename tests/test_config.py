
from backend.config import Settings


def test_app_name_default():
    settings = Settings(_env_file=None)

    assert settings.app_name == "SentinelAI"


def test_app_name_environment_override(monkeypatch):
    monkeypatch.setenv("APP_NAME", "SentinelAI-Test")

    settings = Settings(_env_file=None)

    assert settings.app_name == "SentinelAI-Test"
