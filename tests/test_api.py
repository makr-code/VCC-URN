from fastapi.testclient import TestClient
from app.main import app
from fastapi import Depends, HTTPException, status
import os


# Clean catalog ENV for API tests
os.environ.pop("URN_ALLOWED_DOMAINS", None)
os.environ.pop("URN_ALLOWED_OBJ_TYPES", None)
os.environ.pop("URN_CATALOGS_JSON", None)


def test_api_validate_and_generate_and_resolve():
    client = TestClient(app)

    # validate a generated URN
    payload = {
        "state": "nrw",
        "domain": "bimschg",
        "obj_type": "anlage",
        "local_aktenzeichen": "4711-0815-K1",
        "store": False,
    }
    # Without auth (auth_mode default is none => allowed)
    resp = client.post("/api/v1/generate", json=payload)
    if resp.status_code != 200:
        print(f"Generate failed: {resp.status_code} - {resp.text}")
    assert resp.status_code == 200
    urn = resp.json()["urn"]

    # validate endpoint
    r2 = client.post("/api/v1/validate", json={"urn": urn})
    assert r2.status_code == 200
    assert r2.json()["valid"] is True

    # resolve endpoint should return minimal manifest (not stored)
    r3 = client.get("/api/v1/resolve", params={"urn": urn})
    assert r3.status_code == 200
    assert r3.json()["urn"] == urn


# Dependency override to enforce API key for test
from vcc_urn.security import require_auth as real_require_auth
from fastapi import Header


async def fake_require_auth(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
    if x_api_key != "test-key":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or missing API key")
    return {"sub": "test", "mode": "apikey"}


def test_api_generate_requires_api_key_when_protected():
    client = TestClient(app)
    app.dependency_overrides[real_require_auth] = fake_require_auth

    payload = {
        "state": "by",
        "domain": "bau",
        "obj_type": "gutachten",
        "local_aktenzeichen": "AZ-77",
        "store": True,
    }

    # without key
    r = client.post("/api/v1/generate", json=payload)
    assert r.status_code == 401

    # with key
    r_ok = client.post("/api/v1/generate", json=payload, headers={"X-API-Key": "test-key"})
    assert r_ok.status_code == 200
    urn = r_ok.json()["urn"]

    # cleanup override
    app.dependency_overrides.pop(real_require_auth, None)

    # verify stored manifest can be resolved
    r2 = client.get("/api/v1/resolve", params={"urn": urn})
    assert r2.status_code == 200
    assert r2.json()["urn"] == urn
