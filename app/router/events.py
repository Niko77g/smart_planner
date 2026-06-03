from fastapi import APIRouter, Query, HTTPException, status, Depends
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Annotated
from app.router.auth import get_current_user
from app.db.models import Event, User
from app.db.database import get_db
from app.db.models import Event
from app.my_calendar import CalendarControl, CalendarNotConfigure
from datetime import time
from datetime import date as date_type
from app.predictor import StudyPredict


router = APIRouter(prefix="/events", tags=["events"])

def get_calendar() -> CalendarControl:
    # get instance of Google calendar API
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
    sync_to_google: bool= False

class EventRead(BaseModel):
    id: int
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
def list_events( current_user: Annotated[User, Depends(get_current_user)],
    date_p: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = (select(Event).where(Event.user_id==current_user.id).order_by(Event.event_date, Event.start_time))
    if date_p:
        try:
            event_date = date_type.fromisoformat(date_p)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date")
        query = query.where(Event.event_date == event_date)

    events = db.scalars(query).all()
    return [
        EventRead(
            id=event.id,
            title=event.title,
            start=str(event.start_time),
            end=str(event.end_time),
            date=str(event.event_date),
        )
        for event in events
    ]


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_event( current_user: Annotated[User, Depends(get_current_user)],
    data: EventCreate,
    db: Session = Depends(get_db),
):
    event = Event(
        user_id=current_user.id,
        title=data.title,
        event_date=data.date,
        start_time=data.start,
        end_time=data.end,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    synced = False
    sync_message = "Udalosť bola uložená lokálne."

    if data.sync_to_google:
        try:
            # Create event
            calendar = CalendarControl()
            google_event = calendar.add_event(
                title=data.title,
                start=data.start,
                end=data.end,
                d=data.date,
            )

            event.google_event_id = google_event["id"]
            db.commit()

            synced = True
            sync_message = "Event was synced with google event."

        except CalendarNotConfigure:
            sync_message = "Event was not synced with google event."

    return {
        "id": event.id,
        "title": event.title,
        "synced_to_google": synced,
        "message": sync_message,
    }


@router.delete("/{event_id}", status_code=204)
def delete_event( current_user: Annotated[User, Depends(get_current_user)],
    event_id: int,
    db: Session = Depends(get_db),
):
    # Delete a calendar event
    event = db.scalar(select(Event).where(Event.id == event_id, Event.user_id == current_user.id))
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.google_event_id:
        try:
            calendar = CalendarControl()
            calendar.delete_event(event.google_event_id)
        except CalendarNotConfigure:
            pass
    db.delete(event)
    db.commit()
    return None




@router.get("/search", response_model=EventRead)
def read_event(current_user: Annotated[User, Depends(get_current_user)],
    event_id: int,
    db: Session = Depends(get_db),
):
    # Get a single local event by ID
    event = db.scalar(select(Event).where(Event.id == event_id, Event.user_id == current_user.id))
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return EventRead(
        id=event.id,
        title=event.title,
        start=str(event.start_time),
        end=str(event.end_time),
        date=str(event.event_date),
    )


@router.post("/smart", response_model=SmartEventResponse, status_code=status.HTTP_201_CREATED)
async def create_smart_event( current_user: Annotated[User, Depends(get_current_user)],
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
