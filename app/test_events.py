import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import Base, get_db
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models import Event, Attendee
from datetime import datetime, timedelta
import pytz
import asyncio

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)
TestingSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

@pytest_asyncio.fixture(scope="module")
async def async_client():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_create_event(async_client):
    event_data = {
        "name": "Test Event",
        "location": "Test Location",
        "start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(hours=2)).isoformat(),
        "max_capacity": 10,
        "timezone": "UTC"
    }
    response = await async_client.post("/events", json=event_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Event"
    assert data["location"] == "Test Location"
    assert data["max_capacity"] == 10

@pytest.mark.asyncio
async def test_create_event_invalid_capacity(async_client):
    event_data = {
        "name": "Test Event",
        "location": "Test Location",
        "start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(hours=2)).isoformat(),
        "max_capacity": 0,
        "timezone": "UTC"
    }
    response = await async_client.post("/events", json=event_data)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_register_attendee(async_client):
    event_data = {
        "name": "Event2",
        "location": "Loc2",
        "start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(hours=2)).isoformat(),
        "max_capacity": 2,
        "timezone": "UTC"
    }
    event_resp = await async_client.post("/events", json=event_data)
    event_id = event_resp.json()["id"]
    attendee_data = {"name": "John Doe", "email": "john@example.com"}
    response = await async_client.post(f"/events/{event_id}/register", json=attendee_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"

@pytest.mark.asyncio
async def test_register_attendee_duplicate(async_client):
    event_data = {
        "name": "Event3",
        "location": "Loc3",
        "start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(hours=2)).isoformat(),
        "max_capacity": 2,
        "timezone": "UTC"
    }
    event_resp = await async_client.post("/events", json=event_data)
    event_id = event_resp.json()["id"]
    attendee_data = {"name": "Jane Doe", "email": "jane@example.com"}
    await async_client.post(f"/events/{event_id}/register", json=attendee_data)
    response = await async_client.post(f"/events/{event_id}/register", json=attendee_data)
    assert response.status_code == 400
    assert "Duplicate" in response.json()["detail"] or "duplicate" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_events_pagination(async_client):
    response = await async_client.get("/events?skip=0&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "events" in data

@pytest.mark.asyncio
async def test_get_attendees_pagination(async_client):
    event_data = {
        "name": "Event4",
        "location": "Loc4",
        "start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(hours=2)).isoformat(),
        "max_capacity": 5,
        "timezone": "UTC"
    }
    event_resp = await async_client.post("/events", json=event_data)
    event_id = event_resp.json()["id"]
    for i in range(3):
        attendee_data = {"name": f"User{i}", "email": f"user{i}@example.com"}
        await async_client.post(f"/events/{event_id}/register", json=attendee_data)
    response = await async_client.get(f"/events/{event_id}/attendees?skip=0&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "attendees" in data
    assert len(data["attendees"]) <= 2
