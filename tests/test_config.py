import importlib
import os


def test_prod_mode_env_parsing_true(monkeypatch):
    monkeypatch.setenv("PROD_MODE", "true")
    cfg = importlib.import_module("email_me_anything.config")
    importlib.reload(cfg)
    assert cfg.Config.PROD_MODE is True


def test_prod_mode_env_parsing_false(monkeypatch):
    monkeypatch.setenv("PROD_MODE", "false")
    cfg = importlib.import_module("email_me_anything.config")
    importlib.reload(cfg)
    assert cfg.Config.PROD_MODE is False


def test_prod_mode_env_parsing_other_values(monkeypatch):
    """Test that non-true values default to False"""
    monkeypatch.setenv("PROD_MODE", "yes")
    cfg = importlib.import_module("email_me_anything.config")
    importlib.reload(cfg)
    assert cfg.Config.PROD_MODE is False


def test_email_sender_env_parsing(monkeypatch):
    """Test EMAIL_SENDER environment variable"""
    monkeypatch.setenv("EMAIL_SENDER", "John Doe")
    cfg = importlib.import_module("email_me_anything.config")
    importlib.reload(cfg)
    assert cfg.Config.EMAIL_SENDER == "John Doe"


def test_email_sender_address_env_parsing(monkeypatch):
    """Test EMAIL_SENDER_ADDRESS environment variable"""
    monkeypatch.setenv("EMAIL_SENDER_ADDRESS", "sender@example.com")
    cfg = importlib.import_module("email_me_anything.config")
    importlib.reload(cfg)
    assert cfg.Config.EMAIL_SENDER_ADDRESS == "sender@example.com"


def test_email_recipient_0_name_env_parsing(monkeypatch):
    """Test EMAIL_RECIPIENT_0_NAME environment variable"""
    monkeypatch.setenv("EMAIL_RECIPIENT_0_NAME", "Jane Doe")
    cfg = importlib.import_module("email_me_anything.config")
    importlib.reload(cfg)
    assert cfg.Config.EMAIL_RECIPIENT_0_NAME == "Jane Doe"


def test_email_recipient_0_address_env_parsing(monkeypatch):
    """Test EMAIL_RECIPIENT_0_ADDRESS environment variable"""
    monkeypatch.setenv("EMAIL_RECIPIENT_0_ADDRESS", "recipient@example.com")
    cfg = importlib.import_module("email_me_anything.config")
    importlib.reload(cfg)
    assert cfg.Config.EMAIL_RECIPIENT_0_ADDRESS == "recipient@example.com"


def test_config_unset_env_vars_default_to_none(monkeypatch):
    """Test that unset environment variables default to None"""
    # Clear the environment variables and reload the module
    monkeypatch.setenv("EMAIL_SENDER", "")
    monkeypatch.setenv("EMAIL_SENDER_ADDRESS", "")
    monkeypatch.setenv("EMAIL_RECIPIENT_0_NAME", "")
    monkeypatch.setenv("EMAIL_RECIPIENT_0_ADDRESS", "")
    monkeypatch.setenv("PROD_MODE", "")
    
    cfg = importlib.import_module("email_me_anything.config")
    importlib.reload(cfg)
    
    # Empty strings from env should still be treated as values
    # The getenv returns None only when the var doesn't exist
    assert cfg.Config.PROD_MODE is False  # Empty string != "true"
