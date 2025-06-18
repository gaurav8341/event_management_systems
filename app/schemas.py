from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
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

    @field_validator('name', 'location')
    def not_empty_str(cls, v):
        if not v or (isinstance(v, str) and not v.strip()):
            raise ValueError("Field must not be empty")
        return v

    @model_validator(mode="after")
    def convert_times_to_utc(self):
        tzname = self.timezone or "UTC"
        tz = pytz.timezone(tzname)
        for attr in ["start_time", "end_time"]:
            dt = getattr(self, attr)
            if dt.tzinfo is None:
                dt = tz.localize(dt)
            dt_utc = dt.astimezone(pytz.UTC).replace(tzinfo=None)
            setattr(self, attr, dt_utc)
        return self

    @model_validator(mode="after")
    def check_times_and_capacity(self):
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValueError('start_time must be before end_time')
        if self.max_capacity is not None and self.max_capacity <= 0:
            raise ValueError('max_capacity must be greater than 0')
        return self

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
    @field_validator('name', 'email')
    def not_empty_str(cls, v):
        if not v or (isinstance(v, str) and not v.strip()):
            raise ValueError("Field must not be empty")
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
