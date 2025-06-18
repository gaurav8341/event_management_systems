from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pytz import all_timezones
from .. import schemas, crud, models
from ..database import get_db

router = APIRouter(tags=["Events"])

@router.post(
    "/events",
    response_model=schemas.EventOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new event",
    description="Creates a new event with name, location, start/end time, and max capacity. Times are stored in UTC.",
)
async def create_event(event: schemas.EventCreate, db: AsyncSession = Depends(get_db)):
    if event.timezone not in all_timezones:
        raise HTTPException(status_code=400, detail=f"Invalid timezone: {event.timezone}")
    # Check for unique event name
    from sqlalchemy.future import select
    existing = await db.execute(select(models.Event).where(models.Event.name == event.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"Event with name '{event.name}' already exists.")
    return await crud.create_event(db, event)

@router.get(
    "/events",
    response_model=schemas.EventPagination,
    summary="List all upcoming events",
    description="Lists all upcoming events (end_time > now). Supports pagination and timezone conversion.",
)
async def list_events(
    db: AsyncSession = Depends(get_db),
    timezone: str = Query("Asia/Kolkata", description="Timezone, e.g. 'Asia/Kolkata'"),
    skip: int = 0,
    limit: int = 100,
):
    if timezone not in all_timezones:
        raise HTTPException(status_code=400, detail=f"Invalid timezone: {timezone}")
    return await crud.get_upcoming_events(db, user_tz=timezone, skip=skip, limit=limit)

@router.post(
    "/events/{event_id}/register",
    response_model=schemas.AttendeeOut,
    summary="Register an attendee for an event",
    description="Registers an attendee (name, email) for a specific event. Prevents overbooking and duplicate registration.",
)
async def register_attendee(event_id: int, attendee: schemas.AttendeeCreate, db: AsyncSession = Depends(get_db)):
    result = await crud.register_attendee(db, event_id, attendee)
    if result is None:
        raise HTTPException(status_code=400, detail="Duplicate registration or event not found.")
    if result is False:
        raise HTTPException(status_code=400, detail="Event is full.")
    return result

@router.get(
    "/events/{event_id}/attendees",
    response_model=schemas.AttendeePagination,
    summary="List all attendees for an event",
    description="Returns all registered attendees for an event. Supports pagination and timezone conversion.",
)
async def get_attendees(
    event_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    timezone: str = Query("UTC", description="Timezone, e.g. 'Asia/Kolkata'"),
):
    if timezone not in all_timezones:
        raise HTTPException(status_code=400, detail=f"Invalid timezone: {timezone}")
    return await crud.get_attendees(db, event_id, skip=skip, limit=limit, user_tz=timezone)
