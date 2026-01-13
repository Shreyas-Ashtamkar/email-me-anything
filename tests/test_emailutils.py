from pathlib import Path
import importlib

import pytest


def test_build_context_identity():
    from email_me_anything.emailutils import build_context

    data = {"a": 1, "b": 2}
    assert build_context(data) is data


def test_build_context_variable_map_with_missing_keys():
    from email_me_anything.emailutils import build_context

    data = {"user_name": "John", "email": "john@example.com"}
    var_map = {"name": "user_name", "contact": "email", "city": "city"}
    assert build_context(data, var_map) == {
        "name": "John",
        "contact": "john@example.com",
        "city": "",
    }


def test_build_context_empty_variable_map():
    """Test build_context with empty variable_map"""
    from email_me_anything.emailutils import build_context

    data = {"a": 1, "b": 2}
    result = build_context(data, {})
    assert result == {}


def test_build_context_empty_data():
    """Test build_context with empty data"""
    from email_me_anything.emailutils import build_context

    data = {}
    var_map = {"name": "user_name", "email": "email"}
    result = build_context(data, var_map)
    assert result == {"name": "", "email": ""}


def test_build_html_content_renders(simple_template: Path):
    from email_me_anything.emailutils import build_html_content

    data = {"name": "Ada", "quote": "That brain of mine is something more than merely mortal."}
    html = build_html_content(simple_template, data)
    assert "Ada" in html and "brain of mine" in html


def test_build_html_content_with_variable_map(simple_template: Path):
    """Test build_html_content with variable_map parameter"""
    from email_me_anything.emailutils import build_html_content

    data = {"author": "Ada", "text": "That brain of mine is something more than merely mortal."}
    var_map = {"name": "author", "quote": "text"}
    html = build_html_content(simple_template, data, var_map)
    assert "Ada" in html and "brain of mine" in html


def test_build_html_content_missing_var_raises_keyerror(bad_template_missing_key: Path):
    from email_me_anything.emailutils import build_html_content

    with pytest.raises(KeyError):
        build_html_content(bad_template_missing_key, {"ok": "value"})


def test_build_html_content_nonexistent_template():
    """Test build_html_content with nonexistent template file"""
    from email_me_anything.emailutils import build_html_content

    with pytest.raises(FileNotFoundError):
        build_html_content(Path("/does/not/exist.html"), {"data": "value"})


def test_build_html_content_with_unicode(tmp_path: Path):
    """Test build_html_content with Unicode characters"""
    from email_me_anything.emailutils import build_html_content

    t = tmp_path / "template.html"
    t.write_text("<p>{greeting}</p>", encoding="utf-8")
    
    data = {"greeting": "Hello, 世界! 🌍"}
    html = build_html_content(t, data)
    assert "Hello, 世界! 🌍" in html


def test_send_email_uses_mailersend(fake_mailersend, monkeypatch):
    # Import then reload emailutils after injecting fake module to ensure it binds to the fake
    emailutils = importlib.import_module("email_me_anything.emailutils")
    emailutils = importlib.reload(emailutils)
    
    # Force non-production mode to avoid SMTP
    from email_me_anything.emailutils import Config
    monkeypatch.setattr(Config, "PROD_MODE", False)

    sender = {"email": "from@example.com", "name": "From"}
    recipients = [{"email": "to@example.com", "name": "To"}]
    subject = "Hello"
    html = "<p>Hi</p>"

    resp = emailutils.send_email(sender, recipients, subject, html)
    assert resp["status"] == "debug"


def test_send_email_with_multiple_recipients(fake_mailersend, monkeypatch):
    """Test send_email with multiple recipients"""
    emailutils = importlib.import_module("email_me_anything.emailutils")
    emailutils = importlib.reload(emailutils)
    
    # Force non-production mode
    from email_me_anything.emailutils import Config
    monkeypatch.setattr(Config, "PROD_MODE", False)

    sender = {"email": "from@example.com", "name": "From"}
    recipients = [
        {"email": "to1@example.com", "name": "To1"},
        {"email": "to2@example.com", "name": "To2"},
    ]
    subject = "Hello"
    html = "<p>Hi</p>"

    resp = emailutils.send_email(sender, recipients, subject, html)
    assert resp["status"] == "debug"


def test_send_email_with_empty_recipients(fake_mailersend, monkeypatch):
    """Test send_email with empty recipients list - should work in non-production mode"""
    emailutils = importlib.import_module("email_me_anything.emailutils")
    emailutils = importlib.reload(emailutils)
    
    # Force non-production mode to avoid SMTP issues with empty recipients
    from email_me_anything.emailutils import Config
    monkeypatch.setattr(Config, "PROD_MODE", False)

    sender = {"email": "from@example.com", "name": "From"}
    recipients = []
    subject = "Hello"
    html = "<p>Hi</p>"

    resp = emailutils.send_email(sender, recipients, subject, html)
    assert resp["status"] == "debug"


def test_build_html_content_with_empty_template(tmp_path: Path):
    """Test build_html_content with an empty template file"""
    from email_me_anything.emailutils import build_html_content

    t = tmp_path / "empty.html"
    t.write_text("", encoding="utf-8")
    
    data = {"name": "Alice"}
    html = build_html_content(t, data)
    assert html == ""


def test_build_context_with_none_values():
    """Test build_context handles None values in data"""
    from email_me_anything.emailutils import build_context

    data = {"name": None, "email": "test@example.com"}
    var_map = {"username": "name", "contact": "email"}
    result = build_context(data, var_map)
    assert result == {"username": None, "contact": "test@example.com"}


def test_build_html_content_with_missing_closing_brace(tmp_path: Path):
    """Test build_html_content with malformed template (unclosed variable)"""
    from email_me_anything.emailutils import build_html_content
    import pytest

    t = tmp_path / "malformed.html"
    t.write_text("<p>{name is incomplete", encoding="utf-8")
    
    data = {"name": "Alice"}
    # format_map raises ValueError for malformed template
    with pytest.raises(ValueError):
        html = build_html_content(t, data)


def test_build_html_content_with_extra_variables_in_data(tmp_path: Path):
    """Test build_html_content when data has more variables than template needs"""
    from email_me_anything.emailutils import build_html_content

    t = tmp_path / "template.html"
    t.write_text("<p>{name}</p>", encoding="utf-8")
    
    data = {"name": "Alice", "age": 30, "city": "NYC", "extra": "unused"}
    html = build_html_content(t, data)
    assert "Alice" in html
    assert "extra" not in html  # Unused variables shouldn't appear


def test_build_html_content_with_repeated_variables(tmp_path: Path):
    """Test build_html_content with same variable used multiple times"""
    from email_me_anything.emailutils import build_html_content

    t = tmp_path / "template.html"
    t.write_text("<p>{name}</p><span>{name}</span><div>{name}</div>", encoding="utf-8")
    
    data = {"name": "Alice"}
    html = build_html_content(t, data)
    assert html.count("Alice") == 3


def test_build_context_with_nested_dict_values():
    """Test build_context with dictionary values (should not be special-cased)"""
    from email_me_anything.emailutils import build_context

    data = {"user": {"name": "Alice", "age": 30}, "email": "alice@example.com"}
    var_map = {"user_data": "user", "contact": "email"}
    result = build_context(data, var_map)
    assert result == {"user_data": {"name": "Alice", "age": 30}, "contact": "alice@example.com"}


def test_send_email_non_production_mode(fake_mailersend, monkeypatch, tmp_path):
    """Test send_email in non-production mode writes debug file"""
    emailutils = importlib.import_module("email_me_anything.emailutils")
    emailutils = importlib.reload(emailutils)
    
    # Mock Config to be non-production
    from email_me_anything.emailutils import Config
    monkeypatch.setattr(Config, "PROD_MODE", False)
    
    # Change working directory to tmp_path to avoid polluting workspace
    import os
    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    
    try:
        sender = {"email": "from@example.com", "name": "From"}
        recipients = [{"email": "to@example.com", "name": "To"}]
        subject = "Test"
        html = "<p>Test Email Content</p>"

        resp = emailutils.send_email(sender, recipients, subject, html)
        
        assert resp["status"] == "debug"
        assert resp["message"] == "Email not sent in non-production mode."
        
        # Check debug file was created
        debug_file = tmp_path / "debug-email.html"
        assert debug_file.exists()
        assert debug_file.read_text(encoding="utf-8") == html
    finally:
        os.chdir(original_cwd)


def test_send_email_with_empty_subject(fake_mailersend, monkeypatch):
    """Test send_email with empty subject string"""
    emailutils = importlib.import_module("email_me_anything.emailutils")
    emailutils = importlib.reload(emailutils)
    
    # Force non-production mode
    from email_me_anything.emailutils import Config
    monkeypatch.setattr(Config, "PROD_MODE", False)

    sender = {"email": "from@example.com", "name": "From"}
    recipients = [{"email": "to@example.com", "name": "To"}]
    subject = ""
    html = "<p>Content</p>"

    resp = emailutils.send_email(sender, recipients, subject, html)
    assert resp["status"] == "debug"


def test_send_email_with_empty_html(fake_mailersend, monkeypatch):
    """Test send_email with empty HTML content"""
    emailutils = importlib.import_module("email_me_anything.emailutils")
    emailutils = importlib.reload(emailutils)
    
    # Force non-production mode
    from email_me_anything.emailutils import Config
    monkeypatch.setattr(Config, "PROD_MODE", False)

    sender = {"email": "from@example.com", "name": "From"}
    recipients = [{"email": "to@example.com", "name": "To"}]
    subject = "Test"
    html = ""

    resp = emailutils.send_email(sender, recipients, subject, html)
    assert resp["status"] == "debug"


def test_build_html_content_with_html_special_chars(tmp_path: Path):
    """Test build_html_content preserves HTML special characters in data"""
    from email_me_anything.emailutils import build_html_content

    t = tmp_path / "template.html"
    t.write_text("<p>{content}</p>", encoding="utf-8")
    
    data = {"content": "<script>alert('XSS')</script> & < > \""}
    html = build_html_content(t, data)
    # format_map doesn't escape HTML - it's inserted as-is
    assert "<script>alert('XSS')</script>" in html
