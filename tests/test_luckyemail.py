from pathlib import Path
import importlib

import pytest


def test_send_lucky_email_nonprod_writes_file(sample_csv: Path, simple_template: Path, tmp_path: Path, monkeypatch, fake_mailersend):
    lucky = importlib.import_module("email_me_anything.luckyemail")
    # Ensure non-prod by patching Config
    from email_me_anything.luckyemail import Config as LuckyConfig
    monkeypatch.setattr(LuckyConfig, "PROD_MODE", False)
    
    # Change to tmp_path directory so debug file is written there
    import os
    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    
    try:
        ok = lucky.send_lucky_email(
            sample_csv,
            simple_template,
            recipients=[{"email": "x@example.com", "name": "X"}],
            subject="Test",
        )
        assert ok is True
        debug_file = tmp_path / "debug-email.html"
        assert debug_file.exists() and debug_file.read_text(encoding="utf-8").strip() != ""
    finally:
        os.chdir(original_cwd)


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
    from email_me_anything.luckyemail import Config as LuckyConfig
    monkeypatch.setattr(LuckyConfig, "PROD_MODE", False)

    # Create template that expects different variable names
    template = tmp_path / "template.html"
    template.write_text("<p>{author_name}: {text}</p>", encoding="utf-8")
    
    # Create CSV with different column names
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("name,quote\nBenjamin Franklin,Three may keep a secret if two of them are dead\n", encoding="utf-8")
    
    variable_map = {"author_name": "name", "text": "quote"}
    
    # Change to tmp_path directory
    import os
    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    
    try:
        ok = lucky.send_lucky_email(
            csv_file,
            template,
            recipients=[{"email": "x@example.com", "name": "X"}],
            subject="Quote",
            variable_map=variable_map,
        )
        
        assert ok is True
        debug_file = tmp_path / "debug-email.html"
        html_content = debug_file.read_text(encoding="utf-8")
        assert "Benjamin Franklin" in html_content
        assert "Three may keep a secret" in html_content
    finally:
        os.chdir(original_cwd)


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
    from email_me_anything.luckyemail import Config as LuckyConfig
    monkeypatch.setattr(LuckyConfig, "PROD_MODE", False)
    
    # Mock the Config values
    config = importlib.import_module("email_me_anything.luckyemail")
    monkeypatch.setattr("email_me_anything.luckyemail.Config.EMAIL_SENDER_ADDRESS", "default@example.com")
    monkeypatch.setattr("email_me_anything.luckyemail.Config.EMAIL_SENDER", "Default Sender")
    
    # Change to tmp_path directory
    import os
    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    
    try:
        ok = lucky.send_lucky_email(
            sample_csv,
            simple_template,
        )
        
        assert ok is True
        debug_file = tmp_path / "debug-email.html"
        assert debug_file.exists()
    finally:
        os.chdir(original_cwd)


def test_send_lucky_email_with_none_sender_values(sample_csv: Path, simple_template: Path, monkeypatch, fake_mailersend):
    """Test send_lucky_email when sender values are explicitly None"""
    lucky = importlib.import_module("email_me_anything.luckyemail")
    from email_me_anything.luckyemail import Config as LuckyConfig
    monkeypatch.setattr(LuckyConfig, "PROD_MODE", True)

    calls = {}

    def fake_send_email(sender, recipients, subject, html):
        calls["sender"] = sender
        return {"status": "sent"}

    monkeypatch.setattr(lucky, "send_email", fake_send_email)

    ok = lucky.send_lucky_email(
        sample_csv,
        simple_template,
        sender_address=None,
        sender_name=None,
        recipients=[{"email": "to@example.com", "name": "To"}],
    )

    assert ok is True
    # Should use None values as provided
    assert calls["sender"] == {"email": None, "name": None}


def test_send_lucky_email_template_rendering_error(sample_csv: Path, tmp_path: Path, monkeypatch, fake_mailersend):
    """Test send_lucky_email when template has missing variable"""
    lucky = importlib.import_module("email_me_anything.luckyemail")
    monkeypatch.setattr(lucky, "PROD_MODE", False, raising=False)

    # Template expects a variable that doesn't exist in CSV
    template = tmp_path / "bad_template.html"
    template.write_text("<p>{missing_variable}</p>", encoding="utf-8")

    with pytest.raises(KeyError):
        lucky.send_lucky_email(
            sample_csv,
            template,
            recipients=[{"email": "x@example.com", "name": "X"}],
        )


def test_send_lucky_email_with_empty_variable_map(sample_csv: Path, simple_template: Path, tmp_path: Path, monkeypatch, fake_mailersend):
    """Test send_lucky_email with empty variable_map dictionary"""
    lucky = importlib.import_module("email_me_anything.luckyemail")
    from email_me_anything.luckyemail import Config as LuckyConfig
    monkeypatch.setattr(LuckyConfig, "PROD_MODE", False)
    
    # Change to tmp_path directory
    import os
    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    
    try:
        # Empty variable_map means build_context returns empty dict, causing KeyError
        with pytest.raises(KeyError):
            ok = lucky.send_lucky_email(
                sample_csv,
                simple_template,
                variable_map={},
                recipients=[{"email": "x@example.com", "name": "X"}],
            )
    finally:
        os.chdir(original_cwd)


def test_send_lucky_email_with_multiple_recipients(sample_csv: Path, simple_template: Path, monkeypatch, fake_mailersend):
    """Test send_lucky_email with multiple recipients"""
    lucky = importlib.import_module("email_me_anything.luckyemail")
    from email_me_anything.luckyemail import Config as LuckyConfig
    monkeypatch.setattr(LuckyConfig, "PROD_MODE", True)

    calls = {}

    def fake_send_email(sender, recipients, subject, html):
        calls["recipients"] = recipients
        return {"status": "sent"}

    monkeypatch.setattr(lucky, "send_email", fake_send_email)

    ok = lucky.send_lucky_email(
        sample_csv,
        simple_template,
        recipients=[
            {"email": "to1@example.com", "name": "To1"},
            {"email": "to2@example.com", "name": "To2"},
            {"email": "to3@example.com", "name": "To3"},
        ],
    )

    assert ok is True
    assert len(calls["recipients"]) == 3


def test_send_lucky_email_csv_read_error(tmp_path: Path, simple_template: Path, monkeypatch, fake_mailersend):
    """Test send_lucky_email when CSV file cannot be read"""
    lucky = importlib.import_module("email_me_anything.luckyemail")
    monkeypatch.setattr(lucky, "PROD_MODE", False, raising=False)

    # Use a non-existent file
    missing_csv = tmp_path / "missing.csv"

    ok = lucky.send_lucky_email(
        missing_csv,
        simple_template,
        recipients=[{"email": "x@example.com", "name": "X"}],
    )
    
    assert ok is False


def test_send_lucky_email_with_very_long_subject(sample_csv: Path, simple_template: Path, monkeypatch, fake_mailersend):
    """Test send_lucky_email with very long subject line"""
    lucky = importlib.import_module("email_me_anything.luckyemail")
    from email_me_anything.luckyemail import Config as LuckyConfig
    monkeypatch.setattr(LuckyConfig, "PROD_MODE", True)

    calls = {}

    def fake_send_email(sender, recipients, subject, html):
        calls["subject"] = subject
        return {"status": "sent"}

    monkeypatch.setattr(lucky, "send_email", fake_send_email)

    long_subject = "A" * 1000  # Very long subject

    ok = lucky.send_lucky_email(
        sample_csv,
        simple_template,
        recipients=[{"email": "to@example.com", "name": "To"}],
        subject=long_subject,
    )

    assert ok is True
    assert calls["subject"] == long_subject


def test_send_lucky_email_with_special_characters_in_subject(sample_csv: Path, simple_template: Path, monkeypatch, fake_mailersend):
    """Test send_lucky_email with special characters in subject"""
    lucky = importlib.import_module("email_me_anything.luckyemail")
    from email_me_anything.luckyemail import Config as LuckyConfig
    monkeypatch.setattr(LuckyConfig, "PROD_MODE", True)

    calls = {}

    def fake_send_email(sender, recipients, subject, html):
        calls["subject"] = subject
        return {"status": "sent"}

    monkeypatch.setattr(lucky, "send_email", fake_send_email)

    special_subject = "Test 📧 Email <script>alert('XSS')</script> & 你好"

    ok = lucky.send_lucky_email(
        sample_csv,
        simple_template,
        recipients=[{"email": "to@example.com", "name": "To"}],
        subject=special_subject,
    )

    assert ok is True
    assert calls["subject"] == special_subject


def test_send_lucky_email_empty_recipients_list(sample_csv: Path, simple_template: Path, monkeypatch, fake_mailersend):
    """Test send_lucky_email with empty recipients list"""
    lucky = importlib.import_module("email_me_anything.luckyemail")
    from email_me_anything.luckyemail import Config as LuckyConfig
    monkeypatch.setattr(LuckyConfig, "PROD_MODE", True)

    calls = {}

    def fake_send_email(sender, recipients, subject, html):
        calls["recipients"] = recipients
        return {"status": "sent"}

    monkeypatch.setattr(lucky, "send_email", fake_send_email)

    ok = lucky.send_lucky_email(
        sample_csv,
        simple_template,
        recipients=[],
    )

    assert ok is True
    assert calls["recipients"] == []
