from fastapi import APIRouter, Query, HTTPException, status, Depends
from typing import List, Optional
from pydantic import BaseModel
from app.my_calendar import CalendarControl
from datetime import time
from datetime import date as date_type
from app.predictor import StudyPredict


router = APIRouter(prefix="/events", tags=["events"])

def get_calendar() -> CalendarControl:
    # get instance of google calendar API
    return CalendarControl()

def get_predictor() -> StudyPredict:
    # get instance of predictor
    return StudyPredict()


# Pydantic models
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

class SmartEventCreate(BaseModel):
    subject: str
    task_type: str
    difficulty: int
    pages_count: int
    days_until_test: int
    study_date: date_type
    start_time: time

class SmartEventResponse(BaseModel):
    event_id: str
    title: str
    date: str
    start: str
    end: str
    predicted_minutes: int
    message: str

class PredictRequest(BaseModel):
    subject: str
    task_type: str
    difficulty: int
    pages_count: int
    days_until_test: int

class PredictResponse(BaseModel):
    predicted_minutes: int
    formatted: str
    daily_minutes: int
    days_until_test: int


# Endpoints

@router.get("/", response_model=List[EventRead])
def list_events(
    date_p: Optional[str] = Query(None),
    calendar: CalendarControl = Depends(get_calendar)  # Lazy
):
    #List calendar events
    obj = None
    if date_p:
        try:
            obj = date_type.fromisoformat(date_p)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date")

    items = calendar.list_events(obj)

    out = []
    for item in items:
        start_event = item.get("start", {})
        end_event = item.get("end", {})
        # time vs date
        start_v = start_event.get("dateTime") or start_event.get("date")
        end_v = end_event.get("dateTime") or end_event.get("date")
        if not start_v or not end_v:
            continue
        out.append(EventRead(
            id=item["id"],
            title=item.get("summary", ""),
            start=start_v,
            end=end_v,
            date=item["start"].get("date")
        ))
    return out


@router.post("/", response_model=EventRead, status_code=status.HTTP_201_CREATED)
async def create_event(
    data: EventCreate,
    calendar: CalendarControl = Depends(get_calendar)
):
    #Create a calendar event
    try:
        google_event = calendar.add_event(
            title=data.title,
            start=data.start,
            end=data.end,
            d=data.date
        )
        return EventRead(
            id=google_event["id"],
            title=google_event.get("summary", ""),
            start=google_event["start"].get("dateTime", google_event["start"].get("date")),
            end=google_event["end"].get("dateTime", google_event["end"].get("date")),
            date=google_event["start"].get("date")
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{event_id}", status_code=204)
def delete_event(
    event_id: str,
    calendar: CalendarControl = Depends(get_calendar)
):
    #Delete a calendar event
    calendar.delete_event(event_id)
    return None


@router.get("/search", response_model=EventRead)
def read_event(
    event_id: str,
    calendar: CalendarControl = Depends(get_calendar)
):
    #Get a single event by ID
    event = calendar.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("/smart", response_model=SmartEventResponse, status_code=status.HTTP_201_CREATED)
async def create_smart_event(
    data: SmartEventCreate,
    predictor: StudyPredict = Depends(get_predictor)
):
    #Create a smart calendar event with ML prediction
    try:
        result = predictor.create_study_bridge(
            subject=data.subject,
            task_type=data.task_type,
            difficulty=data.difficulty,
            pages_count=data.pages_count,
            days_until_test=data.days_until_test,
            study_date=data.study_date,
            start_time=data.start_time
        )
        return SmartEventResponse(
            event_id=result["event_id"],
            title=result["title"],
            start=result["start"],
            end=result["end"],
            date=result["date"],
            predicted_minutes=result["predicted_minutes"],
            message=f"Na túto úlohu budeš potrebovať približne {result['predicted_minutes']} minút"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/predict", response_model=PredictResponse)
async def create_predict_event(
    data: PredictRequest,
    predictor: StudyPredict = Depends(get_predictor)
):
    #Get time prediction without creating calendar event
    try:
        minutes = predictor.predict_time(
            subject=data.subject,
            task_type=data.task_type,
            difficulty=data.difficulty,
            pages_count=data.pages_count,
            days_until_test=data.days_until_test
        )
        hours = minutes // 60
        mins = minutes % 60
        formatted = f"{hours}h {mins}min" if hours > 0 else f"{mins}min"
        daily = max(1, minutes // max(1, data.days_until_test))

        return PredictResponse(
            predicted_minutes=minutes,
            formatted=formatted,
            daily_minutes=daily,
            days_until_test=data.days_until_test
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))