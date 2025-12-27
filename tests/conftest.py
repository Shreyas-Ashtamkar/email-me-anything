import types
from pathlib import Path
import sys
import pytest


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    p = tmp_path / "sample.csv"
    p.write_text("name,quote\nAda,Imagination is intelligence with an erection\n", encoding="utf-8")
    return p


@pytest.fixture
def header_only_csv(tmp_path: Path) -> Path:
    p = tmp_path / "header.csv"
    p.write_text("name,quote\n", encoding="utf-8")
    return p


@pytest.fixture
def simple_template(tmp_path: Path) -> Path:
    t = tmp_path / "template.html"
    t.write_text("<html><body><p>{quote}</p><span>{name}</span></body></html>", encoding="utf-8")
    return t


@pytest.fixture
def bad_template_missing_key(tmp_path: Path) -> Path:
    t = tmp_path / "bad.html"
    t.write_text("<div>{missing}</div>", encoding="utf-8")
    return t


@pytest.fixture
def fake_mailersend(monkeypatch):
    """Provide a fake 'mailersend' module injected into sys.modules."""
    mod = types.SimpleNamespace()

    class DummyResponse:
        def __init__(self, payload):
            self._payload = payload

        def to_dict(self):
            return {"status": "ok", "echo": self._payload}

    class DummyEmailsAPI:
        def send(self, email):
            return DummyResponse(email)

    class MailerSendClient:
        def __init__(self):
            self.emails = DummyEmailsAPI()

    class EmailBuilder:
        def __init__(self):
            self._payload = {
                "from": None,
                "to": [],
                "subject": None,
                "html": None,
            }

        def from_email(self, email, name):
            self._payload["from"] = {"email": email, "name": name}
            return self

        def to_many(self, recipients):
            self._payload["to"] = recipients
            return self

        def subject(self, subject):
            self._payload["subject"] = subject
            return self

        def html(self, html):
            self._payload["html"] = html
            return self

        def build(self):
            return self._payload

    mod.MailerSendClient = MailerSendClient
    mod.EmailBuilder = EmailBuilder

    monkeypatch.setitem(sys.modules, "mailersend", mod)
    return mod
