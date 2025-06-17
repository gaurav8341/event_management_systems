from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from . import models, schemas
from typing import List, Optional
from datetime import datetime
from pytz import timezone as pytz_timezone, UTC

# Event CRUD

async def create_event(db: AsyncSession, event: schemas.EventCreate) -> models.Event:
    db_event = models.Event(
        name=event.name,
        location=event.location,
        start_time=event.start_time,
        end_time=event.end_time,
        max_capacity=event.max_capacity
    )
    db.add(db_event)
    await db.commit()
    await db.refresh(db_event)
    return db_event

async def get_upcoming_events(db: AsyncSession, user_tz: str = "UTC", skip: int = 0, limit: int = 100) -> dict:
    now = datetime.utcnow()
    result = await db.execute(select(models.Event).where(models.Event.end_time > now).offset(skip).limit(limit))
    events = result.scalars().all()
    total_result = await db.execute(select(models.Event).where(models.Event.end_time > now))
    total = len(total_result.scalars().all())
    tz = pytz_timezone(user_tz)
    event_list = []
    for event in events:
        event_list.append({
            "id": event.id,
            "name": event.name,
            "location": event.location,
            "start_time": UTC.localize(event.start_time).astimezone(tz).isoformat(),
            "end_time": UTC.localize(event.end_time).astimezone(tz).isoformat(),
            "max_capacity": event.max_capacity
        })
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "events": event_list
    }

# Attendee CRUD

async def register_attendee(db: AsyncSession, event_id: int, attendee: schemas.AttendeeCreate) -> Optional[models.Attendee]:
    result = await db.execute(select(models.Event).where(models.Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        return None
    if len(event.attendees) >= event.max_capacity:
        return False  # Overbooked
    # Prevent duplicate registration for same event/email
    for a in event.attendees:
        if a.email == attendee.email:
            return None
    db_attendee = models.Attendee(
        name=attendee.name,
        email=attendee.email,
        event_id=event_id
    )
    db.add(db_attendee)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        return None
    await db.refresh(db_attendee)
    return db_attendee

async def get_attendees(db: AsyncSession, event_id: int, skip: int = 0, limit: int = 100, user_tz: str = "UTC") -> dict:
    attendees_result = await db.execute(select(models.Attendee).where(models.Attendee.event_id == event_id).offset(skip).limit(limit))
    attendees = attendees_result.scalars().all()
    total_result = await db.execute(select(models.Attendee).where(models.Attendee.event_id == event_id))
    total = len(total_result.scalars().all())
    event_result = await db.execute(select(models.Event).where(models.Event.id == event_id))
    event = event_result.scalar_one_or_none()
    tz = pytz_timezone(user_tz)
    result = []
    for attendee in attendees:
        result.append({
            "id": attendee.id,
            "name": attendee.name,
            "email": attendee.email,
            "event_id": attendee.event_id,
            "event_start_time": UTC.localize(event.start_time).astimezone(tz).isoformat() if event else None,
            "event_end_time": UTC.localize(event.end_time).astimezone(tz).isoformat() if event else None
        })
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "attendees": result
    }
