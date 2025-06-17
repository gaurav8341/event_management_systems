from fastapi import FastAPI
from .database import Base, engine
from .api import events

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)

app.include_router(events.router)

@app.get("/")
def root():
    return {"message": "Event Management System API is up!"}
