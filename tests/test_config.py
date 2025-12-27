import importlib
import os


def test_prod_mode_env_parsing_true(monkeypatch):
    monkeypatch.setenv("PROD_MODE", "true")
    cfg = importlib.import_module("email_me_anything.config")
    importlib.reload(cfg)
    assert cfg.PROD_MODE is True


def test_prod_mode_env_parsing_false(monkeypatch):
    monkeypatch.setenv("PROD_MODE", "false")
    cfg = importlib.import_module("email_me_anything.config")
    importlib.reload(cfg)
    assert cfg.PROD_MODE is False
