from pathlib import Path
import importlib

import pytest


def test_send_lucky_email_nonprod_writes_file(sample_csv: Path, simple_template: Path, tmp_path: Path, monkeypatch, fake_mailersend):
    lucky = importlib.import_module("email_me_anything.luckyemail")
    # Ensure non-prod
    monkeypatch.setattr(lucky, "PROD_MODE", False, raising=False)

    out = tmp_path / "out.html"
    ok = lucky.send_lucky_email(
        sample_csv,
        simple_template,
        recipients=[{"email": "x@example.com", "name": "X"}],
        subject="Test",
        output_html_path=out,
    )
    assert ok is True
    assert out.exists() and out.read_text(encoding="utf-8").strip() != ""


def test_send_lucky_email_no_row_returns_false(monkeypatch, fake_mailersend):
    lucky = importlib.import_module("email_me_anything.luckyemail")
    monkeypatch.setattr(lucky, "PROD_MODE", False, raising=False)
    monkeypatch.setattr(lucky, "select_random_row", lambda p: False)

    ok = lucky.send_lucky_email(Path("/does/not/matter.csv"), Path("/also/ignored.html"))
    assert ok is False


def test_send_lucky_email_prod_calls_send_email(sample_csv: Path, simple_template: Path, monkeypatch, fake_mailersend):
    lucky = importlib.import_module("email_me_anything.luckyemail")
    # Import Config from the luckyemail module to properly monkeypatch it
    from email_me_anything.luckyemail import Config as LuckyConfig
    monkeypatch.setattr(LuckyConfig, "PROD_MODE", True)

    calls = {}

    def fake_send_email(sender, recipients, subject, html):
        calls["args"] = {
            "sender": sender,
            "recipients": recipients,
            "subject": subject,
            "html": html,
        }
        return {"status": "sent"}

    monkeypatch.setattr(lucky, "send_email", fake_send_email)

    ok = lucky.send_lucky_email(
        sample_csv,
        simple_template,
        sender_address="from@example.com",
        sender_name="From",
        recipients=[{"email": "to@example.com", "name": "To"}],
        subject="Hello",
    )

    assert ok is True
    assert calls["args"]["sender"] == {"email": "from@example.com", "name": "From"}
    assert calls["args"]["recipients"] == [{"email": "to@example.com", "name": "To"}]
    assert calls["args"]["subject"] == "Hello"
    assert isinstance(calls["args"]["html"], str) and calls["args"]["html"].strip() != ""


def test_send_lucky_email_with_variable_map(sample_csv: Path, tmp_path: Path, monkeypatch, fake_mailersend):
    """Test send_lucky_email with variable_map to rename CSV columns"""
    lucky = importlib.import_module("email_me_anything.luckyemail")
    monkeypatch.setattr(lucky, "PROD_MODE", False, raising=False)

    # Create template that expects different variable names
    template = tmp_path / "template.html"
    template.write_text("<p>{author_name}: {text}</p>", encoding="utf-8")
    
    # Create CSV with different column names
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("name,quote\nBenjamin Franklin,Three may keep a secret if two of them are dead\n", encoding="utf-8")
    
    out = tmp_path / "out.html"
    variable_map = {"author_name": "name", "text": "quote"}
    
    ok = lucky.send_lucky_email(
        csv_file,
        template,
        recipients=[{"email": "x@example.com", "name": "X"}],
        subject="Quote",
        variable_map=variable_map,
        output_html_path=out,
    )
    
    assert ok is True
    html_content = out.read_text(encoding="utf-8")
    assert "Benjamin Franklin" in html_content
    assert "Three may keep a secret" in html_content


def test_send_lucky_email_default_subject(sample_csv: Path, simple_template: Path, monkeypatch, fake_mailersend):
    """Test send_lucky_email uses default subject when none provided"""
    lucky = importlib.import_module("email_me_anything.luckyemail")
    from email_me_anything.luckyemail import Config as LuckyConfig
    monkeypatch.setattr(LuckyConfig, "PROD_MODE", True)

    calls = {}

    def fake_send_email(sender, recipients, subject, html):
        calls["subject"] = subject
        return {"status": "sent"}

    monkeypatch.setattr(lucky, "send_email", fake_send_email)

    ok = lucky.send_lucky_email(
        sample_csv,
        simple_template,
        recipients=[{"email": "to@example.com", "name": "To"}],
    )

    assert ok is True
    assert calls["subject"] == "New Data Row!"


def test_send_lucky_email_none_row_returns_false(header_only_csv: Path, simple_template: Path, monkeypatch, fake_mailersend):
    """Test send_lucky_email returns False when CSV has only header (no data rows)"""
    lucky = importlib.import_module("email_me_anything.luckyemail")
    monkeypatch.setattr(lucky, "PROD_MODE", False, raising=False)

    ok = lucky.send_lucky_email(
        header_only_csv,
        simple_template,
        recipients=[{"email": "x@example.com", "name": "X"}],
    )
    
    assert ok is False


def test_send_lucky_email_with_default_config_values(sample_csv: Path, simple_template: Path, tmp_path: Path, monkeypatch, fake_mailersend):
    """Test send_lucky_email uses Config defaults when sender/recipient not specified"""
    lucky = importlib.import_module("email_me_anything.luckyemail")
    monkeypatch.setattr(lucky, "PROD_MODE", False, raising=False)
    
    # Mock the Config values
    config = importlib.import_module("email_me_anything.luckyemail")
    monkeypatch.setattr("email_me_anything.luckyemail.Config.EMAIL_SENDER_ADDRESS", "default@example.com")
    monkeypatch.setattr("email_me_anything.luckyemail.Config.EMAIL_SENDER", "Default Sender")

    out = tmp_path / "out.html"
    
    ok = lucky.send_lucky_email(
        sample_csv,
        simple_template,
        output_html_path=out,
    )
    
    assert ok is True
    assert out.exists()
