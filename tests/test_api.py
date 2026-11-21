import json
import logging

import pytest
from fastapi.testclient import TestClient

from mitra import api
from mitra.agent import Assistant
from mitra.kb import KnowledgeBase
from mitra.logging_setup import JsonFormatter
from mitra.seed import CitizenStore

KEY = {"X-API-Key": "key-one"}


@pytest.fixture()
def client(assistant):
    """Open API (development, no keys)."""
    with TestClient(api.create_app(api_keys=set(), production=False, assistant=assistant)) as c:
        yield c


@pytest.fixture()
def secured(assistant):
    with TestClient(api.create_app(api_keys={"key-one", "key-two"}, production=False, assistant=assistant)) as c:
        yield c


# ---- basic behaviour --------------------------------------------------------------------------

def test_health_and_ready(client):
    assert client.get("/health").json() == {"status": "ok"}
    ready = client.get("/ready")
    assert ready.status_code == 200 and ready.json()["documents"] > 50


def test_schemes_lists_the_three_supported_schemes(client):
    assert {s["scheme_id"] for s in client.get("/schemes").json()} == {"SCH-FRM-01", "SCH-FRM-02", "SCH-PEN-01"}


def test_eligibility_for_a_seed_citizen_is_date_aware(client):
    def outcome(as_of):
        response = client.post("/eligibility", json={"scheme_id": "SCH-PEN-01", "citizen_id": "C1021", "as_of": as_of})
        assert response.status_code == 200
        return response.json()["outcome"]

    assert outcome("2026-11-21") == "meets_criteria"
    assert outcome("2026-09-09") == "does_not_meet"


def test_eligibility_accepts_an_inline_profile(client):
    response = client.post("/eligibility", json={
        "scheme_id": "SCH-FRM-01", "as_of": "2026-11-21",
        "profile": {"occupation": "farmer", "land_holding_acres": 3, "residence_type": "rural"}})
    assert response.json()["outcome"] == "meets_criteria"
    assert "makes the final decision" in response.json()["disclaimer"]


@pytest.mark.parametrize("payload, status", [
    ({"scheme_id": "SCH-XXX-99", "profile": {"age": 70}}, 404),
    ({"scheme_id": "SCH-PEN-01", "citizen_id": "C9999"}, 404),
    ({"scheme_id": "SCH-PEN-01"}, 422),
    ({"scheme_id": "SCH-PEN-01", "profile": {"annual_household_income": "lots"}}, 422),
    ({"scheme_id": "SCH-PEN-01", "profile": {f"k{i}": 1 for i in range(21)}}, 422),   # too many keys
    ({"scheme_id": "SCH-PEN-01", "profile": {"occupation": "x" * 101}}, 422),          # value too long
    ({"scheme_id": "SCH-PEN-01", "citizen_id": "C1021; DROP TABLE"}, 422),             # malformed id
])
def test_eligibility_errors(client, payload, status):
    assert client.post("/eligibility", json=payload).status_code == status


def test_eligibility_refuses_a_citizen_without_consent(client, assistant, monkeypatch):
    record = {"citizen_id": "CX", "consent_given": "N", "date_of_birth": "1950-01-01"}
    monkeypatch.setattr(assistant, "citizens", CitizenStore({"CX": record}))
    assert client.post("/eligibility", json={"scheme_id": "SCH-PEN-01", "citizen_id": "CX"}).status_code == 403


def test_chat_returns_a_structured_answer(client):
    body = client.post("/chat", json={"message": "Someone asked me for my OTP", "as_of": "2026-11-21"}).json()
    assert body["intent"] == "fraud" and body["escalate_to"] == "fraud_desk" and "POL-FEE-01" in body["citations"]


def test_chat_validates_input(client):
    assert client.post("/chat", json={"message": ""}).status_code == 422
    assert client.post("/chat", json={"message": "x" * 2001}).status_code == 422
    assert client.post("/chat", json={"message": "hi", "language": "fr"}).status_code == 422
    bad_profile = {"message": "Am I eligible for pension?", "profile": {"age": "old"}}
    assert client.post("/chat", json=bad_profile).status_code == 422


# ---- authentication ---------------------------------------------------------------------------

PROTECTED = [("get", "/schemes", None), ("post", "/eligibility", {"scheme_id": "SCH-PEN-01", "profile": {"age": 70}}),
             ("post", "/chat", {"message": "hello"})]


@pytest.mark.parametrize("method, path, body", PROTECTED)
def test_protected_endpoints_reject_missing_and_wrong_keys(secured, method, path, body):
    for headers in ({}, {"X-API-Key": "nope"}, {"X-API-Key": ""}, {"X-API-Key": "key-one "}):
        response = getattr(secured, method)(path, headers=headers, **({"json": body} if body else {}))
        assert response.status_code == 401 and response.headers["www-authenticate"] == "ApiKey"


@pytest.mark.parametrize("method, path, body", PROTECTED)
def test_protected_endpoints_accept_any_configured_key(secured, method, path, body):
    for key in ("key-one", "key-two"):
        response = getattr(secured, method)(path, headers={"X-API-Key": key}, **({"json": body} if body else {}))
        assert response.status_code == 200


def test_health_and_ready_stay_open_for_orchestrators(secured):
    assert secured.get("/health").status_code == 200 and secured.get("/ready").status_code == 200


def test_non_ascii_key_is_rejected_not_a_server_error(secured):
    assert secured.get("/schemes", headers={"X-API-Key": "clé-ünïcode".encode("utf-8")}).status_code == 401


# ---- production mode --------------------------------------------------------------------------

def test_production_refuses_to_start_without_api_keys():
    with pytest.raises(RuntimeError, match="MITRA_API_KEYS"):
        api.create_app(api_keys=set(), production=True)


def test_production_hides_interactive_docs(assistant):
    with TestClient(api.create_app(api_keys={"k"}, production=True, assistant=assistant)) as prod:
        assert prod.get("/docs").status_code == 404 and prod.get("/openapi.json").status_code == 404


def test_development_serves_interactive_docs(client):
    assert client.get("/docs").status_code == 200


def test_production_refuses_to_start_on_an_unhealthy_knowledge_base():
    empty = Assistant(KnowledgeBase([]), CitizenStore({}))
    with pytest.raises(RuntimeError, match="missing required document"):
        with TestClient(api.create_app(api_keys={"k"}, production=True, assistant=empty)):
            pass


def test_development_starts_unhealthy_but_reports_not_ready():
    empty = Assistant(KnowledgeBase([]), CitizenStore({}))
    with TestClient(api.create_app(api_keys=set(), production=False, assistant=empty)) as c:
        response = c.get("/ready")
        assert response.status_code == 503
        assert "missing required document GL-PEN-01" in response.json()["problems"]


# ---- request handling -------------------------------------------------------------------------

def test_every_response_has_request_id_and_privacy_headers(client):
    response = client.get("/health")
    assert len(response.headers["x-request-id"]) == 32
    assert response.headers["cache-control"] == "no-store" and response.headers["x-content-type-options"] == "nosniff"


def test_valid_inbound_request_id_is_kept_and_bad_one_replaced(client):
    assert client.get("/health", headers={"X-Request-ID": "trace-abc_123"}).headers["x-request-id"] == "trace-abc_123"
    replaced = client.get("/health", headers={"X-Request-ID": "bad id\twith spaces"}).headers["x-request-id"]
    assert replaced != "bad id\twith spaces" and len(replaced) == 32


def test_unhandled_errors_return_a_generic_500_without_details(assistant):
    app = api.create_app(api_keys=set(), production=False, assistant=assistant)
    app.add_api_route("/boom", lambda: 1 / 0)
    with TestClient(app, raise_server_exceptions=False) as c:
        response = c.get("/boom")
    body = response.json()
    assert response.status_code == 500 and body["detail"] == "Internal server error."
    assert "division" not in response.text and body["request_id"] == response.headers["x-request-id"]


def test_cors_is_off_by_default_and_opt_in(assistant):
    preflight = {"Origin": "https://portal.example.org", "Access-Control-Request-Method": "POST"}
    with TestClient(api.create_app(api_keys=set(), production=False, assistant=assistant)) as closed:
        assert "access-control-allow-origin" not in closed.options("/chat", headers=preflight).headers
    with TestClient(api.create_app(api_keys=set(), production=False, assistant=assistant,
                                   cors_origins=["https://portal.example.org"])) as opened:
        allowed = opened.options("/chat", headers=preflight)
        assert allowed.headers["access-control-allow-origin"] == "https://portal.example.org"
        other = opened.options("/chat", headers={**preflight, "Origin": "https://evil.example.com"})
        assert "access-control-allow-origin" not in other.headers


# ---- logging privacy --------------------------------------------------------------------------

class _Capture(logging.Handler):
    def __init__(self):
        super().__init__()
        self.lines: list[str] = []

    def emit(self, record):
        self.lines.append(JsonFormatter().format(record))


def test_logs_contain_metadata_but_never_message_text_profile_values_or_citizen_ids(client):
    capture = _Capture()
    logger = logging.getLogger("mitra")
    logger.addHandler(capture)
    try:
        secret = "ZEBRA-SECRET-MESSAGE-7731"
        chat = client.post("/chat", json={"message": f"{secret} my income is ₹1,35,000 am I eligible for pension?",
                                          "citizen_id": "C1021", "as_of": "2026-11-21"})
        client.post("/eligibility", json={"scheme_id": "SCH-PEN-01", "citizen_id": "C1021",
                                          "profile": {"annual_household_income": 987654}})
        client.post("/chat", json={"message": "Someone asked for my OTP"})
    finally:
        logger.removeHandler(capture)
    text = "\n".join(capture.lines)
    for private in (secret, "1,35,000", "C1021", "987654", "OTP"):
        assert private not in text, f"{private!r} leaked into logs"
    records = [json.loads(line) for line in capture.lines]
    assert all("request_id" in r for r in records)
    chat_log = next(r for r in records if r["msg"] == "chat")
    assert chat_log["intent"] == "eligibility" and chat_log["scheme_id"] == "SCH-PEN-01"
    assert chat_log["request_id"] == chat.headers["x-request-id"]
    assert any(r["msg"] == "escalation" and r["escalate_to"] == "fraud_desk" for r in records)
    assert any(r["msg"] == "request" and r["path"] == "/chat" and r["status"] == 200 for r in records)
