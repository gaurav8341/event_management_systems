# Event Management System (Async FastAPI)

## Overview
This is a mini event management backend API built with FastAPI (async), SQLAlchemy, and SQLite (or PostgreSQL). It allows users to create events, register attendees, and view attendee lists per event, with robust validation, pagination, and timezone support.

## Features
- Create, list, and paginate events
- Register attendees (with overbooking and duplicate prevention)
- List attendees for an event (with pagination)
- All event times stored in UTC, with timezone conversion in API responses
- Async database operations for high concurrency
- OpenAPI/Swagger documentation at `/docs`
- Unit tests with pytest and pytest-asyncio

## Tech Stack
- FastAPI (async)
- SQLAlchemy (async)
- SQLite (default, can use PostgreSQL)
- Alembic (for migrations)
- Pydantic (validation)
- Pytest, pytest-asyncio (testing)

## Setup
1. **Clone the repo & activate your virtual environment**
   ```bash
   git clone <repo-url>
   cd event_management_systems
   workon omnify  # or source venv/bin/activate
   ```
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the app**
   ```bash
   uvicorn app.main:app --reload
   ```
4. **Access API docs**
   - Open [http://localhost:8000/docs](http://localhost:8000/docs)

## API Endpoints
### Events
- `POST /events` — Create a new event
- `GET /events` — List all upcoming events (supports `skip`, `limit`, `timezone`)

### Attendees
- `POST /events/{event_id}/register` — Register an attendee for an event
- `GET /events/{event_id}/attendees` — List attendees for an event (supports `skip`, `limit`, `timezone`)

## Validation & Error Handling
- All fields are required and validated (no empty strings, valid email, etc.)
- `max_capacity` must be > 0
- `start_time` must be before `end_time`
- Duplicate attendee registration for the same event is prevented (DB constraint)
- Overbooking is prevented

## Timezone Support
- All event times are stored in UTC
- API responses convert times to the requested timezone (default: UTC)
- Pass `timezone` query param (e.g., `Asia/Kolkata`)

## Pagination
- Both event and attendee list endpoints support `skip` and `limit` query params
- Responses include `total`, `skip`, `limit`, and the data list

## Testing
- Run all tests:
  ```bash
  pytest app/
  ```
- Tests cover event creation, attendee registration, duplicate/overbooking prevention, and pagination

## Migrations
This project uses Alembic for database migrations. To manage schema changes:

1. **Initialize Alembic (first time only):**
   ```bash
   alembic init alembic
   ```
   - Edit `alembic.ini` and set your database URL (e.g., `sqlite+aiosqlite:///./app/event_management.db`).
   - In `alembic/env.py`, import your Base and set `target_metadata`:
     ```python
     from app.database import Base
     target_metadata = Base.metadata
     ```

2. **Create a migration after model changes:**
   ```bash
   alembic revision --autogenerate -m "Describe your change"
   ```

3. **Apply migrations to the database:**
   ```bash
   alembic upgrade head
   ```

Repeat steps 2 and 3 whenever you change your models.

## Deployment
- Ready for Dockerization and cloud deployment
- Can be configured for PostgreSQL by changing the DB URL in `app/database.py`

## Security
- No authentication by default (add as needed)

## License
MIT
