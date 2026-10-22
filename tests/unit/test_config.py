import pytest

from nexus_mcp.config import Settings, load_settings, require_auth_settings


def test_port_falls_back_to_PORT(monkeypatch):
    monkeypatch.delenv("NEXUS_PORT", raising=False)
    monkeypatch.setenv("PORT", "9100")
    assert load_settings().port == 9100


def test_required_scopes_accept_commas_and_spaces(monkeypatch):
    monkeypatch.setenv("AUTH_REQUIRED_SCOPES", "a/b, c/d e/f")
    assert load_settings().auth_required_scopes == ("a/b", "c/d", "e/f")


def test_server_refuses_to_start_without_auth_config():
    settings = Settings(host="h", port=1, public_url=None, audit_file_path="x")
    with pytest.raises(RuntimeError):
        require_auth_settings(settings)