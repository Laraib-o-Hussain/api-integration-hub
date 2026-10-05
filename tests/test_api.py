import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def _override_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _sample():
    return {
        "patient_name": "Ava Chen",
        "patient_id": "P-1001",
        "doctor_name": "Dr. Rivera",
        "appointment_date": "2026-10-15",
        "appointment_time": "09:30",
        "status": "scheduled",
    }


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_create_appointment(client):
    r = client.post("/appointments", json=_sample())
    assert r.status_code == 201
    body = r.json()
    assert body["id"] >= 1
    assert body["patient_name"] == "Ava Chen"
    assert body["sync_status"] == "not_synced"


def test_get_appointment(client):
    created = client.post("/appointments", json=_sample()).json()
    r = client.get(f"/appointments/{created['id']}")
    assert r.status_code == 200
    assert r.json()["patient_id"] == "P-1001"


def test_update_appointment(client):
    created = client.post("/appointments", json=_sample()).json()
    r = client.put(
        f"/appointments/{created['id']}",
        json={"status": "confirmed", "appointment_time": "11:00"},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "confirmed"
    assert r.json()["appointment_time"] == "11:00"


def test_delete_appointment(client):
    created = client.post("/appointments", json=_sample()).json()
    r = client.delete(f"/appointments/{created['id']}")
    assert r.status_code == 200
    assert client.get(f"/appointments/{created['id']}").status_code == 404


def test_invalid_date(client):
    bad = _sample()
    bad["appointment_date"] = "15-10-2026"
    r = client.post("/appointments", json=bad)
    assert r.status_code == 422


def test_missing_required_field(client):
    bad = _sample()
    del bad["patient_name"]
    r = client.post("/appointments", json=bad)
    assert r.status_code == 422


def test_nonexistent_appointment(client):
    assert client.get("/appointments/9999").status_code == 404
    assert client.put("/appointments/9999", json={"status": "confirmed"}).status_code == 404
    assert client.delete("/appointments/9999").status_code == 404
    assert client.post("/appointments/9999/sync").status_code == 404


def test_sync_endpoint(client):
    created = client.post("/appointments", json=_sample()).json()
    r = client.post(f"/appointments/{created['id']}/sync")
    assert r.status_code == 200
    body = r.json()
    assert body["sync_status"] == "synced"
    assert body["external_reference"].startswith("EXT-")
    assert body["appointment"]["status"] == "synced"
