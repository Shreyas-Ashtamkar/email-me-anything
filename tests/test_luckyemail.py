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
    monkeypatch.setattr(lucky, "PROD_MODE", True, raising=False)

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
