import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.models import Event, Attendee
from datetime import datetime, timedelta
import pytz

client = TestClient(app)

# Use a test database (in-memory SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[app.get_db] = override_get_db

def test_create_event():
    event_data = {
        "name": "Test Event",
        "location": "Test Location",
        "start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(hours=2)).isoformat(),
        "max_capacity": 10,
        "timezone": "UTC"
    }
    response = client.post("/events", json=event_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Event"
    assert data["location"] == "Test Location"
    assert data["max_capacity"] == 10


def test_create_event_invalid_capacity():
    event_data = {
        "name": "Test Event",
        "location": "Test Location",
        "start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(hours=2)).isoformat(),
        "max_capacity": 0,
        "timezone": "UTC"
    }
    response = client.post("/events", json=event_data)
    assert response.status_code == 422


def test_register_attendee():
    # Create event first
    event_data = {
        "name": "Event2",
        "location": "Loc2",
        "start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(hours=2)).isoformat(),
        "max_capacity": 2,
        "timezone": "UTC"
    }
    event_resp = client.post("/events", json=event_data)
    event_id = event_resp.json()["id"]
    attendee_data = {"name": "John Doe", "email": "john@example.com"}
    response = client.post(f"/events/{event_id}/register", json=attendee_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"


def test_register_attendee_duplicate():
    # Create event first
    event_data = {
        "name": "Event3",
        "location": "Loc3",
        "start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(hours=2)).isoformat(),
        "max_capacity": 2,
        "timezone": "UTC"
    }
    event_resp = client.post("/events", json=event_data)
    event_id = event_resp.json()["id"]
    attendee_data = {"name": "Jane Doe", "email": "jane@example.com"}
    client.post(f"/events/{event_id}/register", json=attendee_data)
    response = client.post(f"/events/{event_id}/register", json=attendee_data)
    assert response.status_code == 400
    assert "Duplicate" in response.json()["detail"] or "duplicate" in response.json()["detail"]


def test_get_events_pagination():
    response = client.get("/events?skip=0&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "events" in data


def test_get_attendees_pagination():
    # Create event and register attendees
    event_data = {
        "name": "Event4",
        "location": "Loc4",
        "start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(hours=2)).isoformat(),
        "max_capacity": 5,
        "timezone": "UTC"
    }
    event_resp = client.post("/events", json=event_data)
    event_id = event_resp.json()["id"]
    for i in range(3):
        attendee_data = {"name": f"User{i}", "email": f"user{i}@example.com"}
        client.post(f"/events/{event_id}/register", json=attendee_data)
    response = client.get(f"/events/{event_id}/attendees?skip=0&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "attendees" in data
    assert len(data["attendees"]) <= 2
