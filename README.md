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

## API Documentation

### 1. Create Event:

**cURL Query**:

```sh
curl --location 'http://localhost:8000/events' \
--header 'Content-Type: application/json' \
--header 'Accept: application/json' \
--data '{
  "name": "WebFest",
  "location": "India",
  "start_time": "2025-08-15T16:18:36.333Z",
  "end_time": "2025-08-20T16:18:36.333Z",
  "max_capacity": 100,
  "timezone": "Asia/Kolkata"
}'
```


**1. Unsuccessfull Response**:

**Code**: 400
**Response**:
```json
{
    "detail": "Event with name 'WebFest' already exists."
}
```

**2. Successfull Response**:

**Code**: 200
**Response**:
```json
{
    "name": "Webfest",
    "location": "est",
    "start_time": "2025-08-15T21:48:36.333000",
    "end_time": "2025-08-20T21:48:36.333000",
    "max_capacity": 100,
    "id": 2
}
```

### 2. Register for Events:

**cURL Query**:

```sh
curl --location 'http://localhost:8000/events/1/register' \
--header 'Content-Type: application/json' \
--header 'Accept: application/json' \
--data-raw '{
  "name": "qwerty",
  "email": "abc.asd@gmail.com"
}'
```

**1. Unsuccessfull Response**:

**Code**: 400
**Response**:
```json
{
    "detail": "Duplicate registration or event not found."
}
```

**2. Successfull Response**:

**Code**: 200
**Response**:
```json
{
    "name": "qwerty",
    "email": "abc1.asd@gmail.com",
    "id": 3,
    "event_id": 1
}
```

### 3. List all events:

**cURL Query**:
```sh
curl --location 'http://localhost:8000/events?timezone=Asia%2FDhaka&skip=0&limit=100' \
--header 'Accept: application/json'
```

**Response**:
```json
{
    "total": 2,
    "skip": 0,
    "limit": 100,
    "events": [
        {
            "id": 1,
            "name": "ut exercitation Ut",
            "location": "est",
            "start_time": "2025-08-16T03:48:36.333000+06:00",
            "end_time": "2025-08-21T03:48:36.333000+06:00",
            "max_capacity": 100
        },
        {
            "id": 2,
            "name": "Webfest",
            "location": "est",
            "start_time": "2025-08-16T03:48:36.333000+06:00",
            "end_time": "2025-08-21T03:48:36.333000+06:00",
            "max_capacity": 100
        }
    ]
}
```

### 4. List all attendees for event

**cURL Query**:
```sh
curl --location 'http://localhost:8000/events/1/attendees?skip=0&limit=100&timezone=UTC' \
--header 'Accept: application/json'
```

**Response**:
```json
{
    "total": 3,
    "skip": 0,
    "limit": 100,
    "attendees": [
        {
            "id": 2,
            "name": "qwerty",
            "email": "abc.asd@gmail.com",
            "event_id": 1,
            "event_start_time": "2025-08-15T21:48:36.333000+00:00",
            "event_end_time": "2025-08-20T21:48:36.333000+00:00"
        },
        {
            "id": 3,
            "name": "qwerty",
            "email": "abc1.asd@gmail.com",
            "event_id": 1,
            "event_start_time": "2025-08-15T21:48:36.333000+00:00",
            "event_end_time": "2025-08-20T21:48:36.333000+00:00"
        },
        {
            "id": 1,
            "name": "dolor",
            "email": "cq12cqMMTR@zfhjju.xnln",
            "event_id": 1,
            "event_start_time": "2025-08-15T21:48:36.333000+00:00",
            "event_end_time": "2025-08-20T21:48:36.333000+00:00"
        }
    ]
}
```



## Deployment
- Ready for Dockerization and cloud deployment
- Can be configured for PostgreSQL by changing the DB URL in `app/database.py`

## Security
- No authentication by default (add as needed)

## License
MIT
