from fastapi import APIRouter, Query, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from app.calendar import CalendarControl
from datetime import date, time


router = APIRouter(prefix="/events", tags=["events"])
calendar = CalendarControl()
class EventCreate(BaseModel):
    title: str
    date: date
    start: time
    end: time

class EventRead(BaseModel):
    id: str
    title: str
    start: str
    end: str
    date: Optional[str] = None


@router.get("/", response_model=List[EventRead])
def list_events(date: Optional[str] = Query(None) ):
    items = calendar.list_events(date)

    out = []
    for item in items:
        out.append(EventRead(
            id = item["id"],
            title = item.get("summary", ""),
            start = item["start"].get("datetime", item["start"].get("date")),
            end = item["end"].get("datetime", item["end"].get("date")),
            date = item["start"].get("date")
        ))
    return out

@router.post("/", response_model=EventRead, status_code=201)
async def create_event(data: EventCreate):
    data_e = calendar.add_event(data.title, data.start, data.end, data.date)
    if data_e is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return data_e


@router.delete("/{id}", status_code=204)
def delete_event(id: str):
    rem_event = calendar.remove_event(id)
    if not rem_event:
        raise HTTPException(status_code=404, detail="Event not found")
    return None

@router.get("/search", response_model=EventRead)
def read_event(id: str):
    event = calendar.get_events_by_id(id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


