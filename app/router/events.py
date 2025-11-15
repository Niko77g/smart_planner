from fastapi import APIRouter, Query, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from app.calendar import CalendarControl
from datetime import time
from datetime import date as date_type


router = APIRouter(prefix="/events", tags=["events"])
calendar = CalendarControl()
class EventCreate(BaseModel):
    title: str
    date: date_type
    start: time
    end: time

class EventRead(BaseModel):
    id: str
    title: str
    start: str
    end: str
    date: Optional[str] = None


@router.get("/", response_model=List[EventRead])
def list_events(date_p: Optional[str] = Query(None) ):
    obj = None
    if date_p:
        try:
            obj = date_type.fromisoformat(date_p)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date")

    items = calendar.list_events(obj)

    out = []
    for item in items:
        start_event = item.get("start",{})
        end_event = item.get("end",{})
        start_v = start_event.get("dateTime")or start_event.get("date")
        end_v = end_event.get("dateTime")or end_event.get("date")
        if not start_v or not end_v:
            continue
        out.append(EventRead(
            id = item["id"],
            title = item.get("summary", ""),
            start = start_v,
            end = end_v,
            date = item["start"].get("date")
        ))
    return out

@router.post("/", response_model=EventRead, status_code=status.HTTP_201_CREATED)
async def create_event(data: EventCreate):

    try:
        google_event =calendar.add_event(title=data.title, start=data.start, end=data.end, d=data.date)
        return EventRead(
            id=google_event["id"],
            title=google_event.get("summary", ""),
            start=google_event["start"].get("dateTime", google_event["start"].get("date")),
            end=google_event["end"].get("dateTime", google_event["end"].get("date")),
            date=google_event["start"].get("date")
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.delete("/{id}", status_code=204)
def delete_event(event_id: str):
    calendar.delete_event(event_id)

    return None

@router.get("/search", response_model=EventRead)
def read_event(event_id: str):
    event = calendar.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


