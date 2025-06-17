from pydantic import BaseModel, EmailStr, Field, validator, root_validator
from datetime import datetime
from typing import List, Optional, Dict, Any
import pytz

class EventBase(BaseModel):
    name: str = Field(...)
    location: str = Field(...)
    start_time: datetime
    end_time: datetime
    max_capacity: int

class EventCreate(EventBase):
    timezone: Optional[str] = "UTC"

    @validator('name', 'location', pre=True, always=True)
    def not_empty_str(cls, v, field):
        if not v or (isinstance(v, str) and not v.strip()):
            raise ValueError(f"{field.name} must not be empty")
        return v

    @validator('start_time', 'end_time', pre=True)
    def convert_to_utc(cls, value, values, field):
        tzname = values.get('timezone', 'UTC')
        tz = pytz.timezone(tzname)
        if value.tzinfo is None:
            # Assume naive datetime is in the user's timezone
            value = tz.localize(value)
        # Convert to UTC
        return value.astimezone(pytz.UTC).replace(tzinfo=None)

    @root_validator
    def check_times_and_capacity(cls, values):
        start = values.get('start_time')
        end = values.get('end_time')
        max_capacity = values.get('max_capacity')
        if start and end and start >= end:
            raise ValueError('start_time must be before end_time')
        if max_capacity is not None and max_capacity <= 0:
            raise ValueError('max_capacity must be greater than 0')
        return values

class EventOut(EventBase):
    id: int
    class Config:
        orm_mode = True

class EventPagination(BaseModel):
    total: int
    skip: int
    limit: int
    events: List[Dict[str, Any]]

class AttendeeBase(BaseModel):
    name: str
    email: EmailStr

class AttendeeCreate(AttendeeBase):
    @validator('name', 'email', pre=True, always=True)
    def not_empty_str(cls, v, field):
        if not v or (isinstance(v, str) and not v.strip()):
            raise ValueError(f"{field.name} must not be empty")
        return v

class AttendeeOut(AttendeeBase):
    id: int
    event_id: int
    class Config:
        orm_mode = True

class AttendeePagination(BaseModel):
    total: int
    skip: int
    limit: int
    attendees: List[Dict[str, Any]]
