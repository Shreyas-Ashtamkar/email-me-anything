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


def test_build_html_content_renders(simple_template: Path):
    from email_me_anything.emailutils import build_html_content

    data = {"name": "Ada", "quote": "That brain of mine is something more than merely mortal."}
    html = build_html_content(simple_template, data)
    assert "Ada" in html and "brain of mine" in html


def test_build_html_content_missing_var_raises_keyerror(bad_template_missing_key: Path):
    from email_me_anything.emailutils import build_html_content

    with pytest.raises(KeyError):
        build_html_content(bad_template_missing_key, {"ok": "value"})


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
