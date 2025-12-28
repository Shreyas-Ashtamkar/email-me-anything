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


def test_send_email_uses_mailersend(fake_mailersend):
    # Import then reload emailutils after injecting fake module to ensure it binds to the fake
    emailutils = importlib.import_module("email_me_anything.emailutils")
    emailutils = importlib.reload(emailutils)

    sender = {"email": "from@example.com", "name": "From"}
    recipients = [{"email": "to@example.com", "name": "To"}]
    subject = "Hello"
    html = "<p>Hi</p>"

    resp = emailutils.send_email(sender, recipients, subject, html)
    assert resp["status"] == "ok"
    echoed = resp["echo"]
    assert echoed["from"] == sender
    assert echoed["to"] == recipients
    assert echoed["subject"] == subject
    assert echoed["html"] == html


def test_send_email_with_multiple_recipients(fake_mailersend):
    """Test send_email with multiple recipients"""
    emailutils = importlib.import_module("email_me_anything.emailutils")
    emailutils = importlib.reload(emailutils)

    sender = {"email": "from@example.com", "name": "From"}
    recipients = [
        {"email": "to1@example.com", "name": "To1"},
        {"email": "to2@example.com", "name": "To2"},
    ]
    subject = "Hello"
    html = "<p>Hi</p>"

    resp = emailutils.send_email(sender, recipients, subject, html)
    assert resp["status"] == "ok"
    assert resp["echo"]["to"] == recipients


def test_send_email_with_empty_recipients(fake_mailersend):
    """Test send_email with empty recipients list"""
    emailutils = importlib.import_module("email_me_anything.emailutils")
    emailutils = importlib.reload(emailutils)

    sender = {"email": "from@example.com", "name": "From"}
    recipients = []
    subject = "Hello"
    html = "<p>Hi</p>"

    resp = emailutils.send_email(sender, recipients, subject, html)
    assert resp["status"] == "ok"
