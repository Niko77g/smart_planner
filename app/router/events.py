from datetime import date as date_type
from datetime import datetime, time, timedelta
from typing import Annotated
from typing import List, Optional
from math import ceil
from fastapi import APIRouter, Query, HTTPException, status, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Event
from app.db.models import User
from app.my_calendar import CalendarControl, CalendarNotConfigure
from app.predictor import StudyPredict
from app.router.auth import get_current_user

router = APIRouter(prefix="/events", tags=["events"])

def get_calendar() -> CalendarControl:
    # get instance of Google calendar API
    return CalendarControl()

def get_predictor() -> StudyPredict:
    # get instance of predictor
    return StudyPredict()


# Pydantic models
class StudyPlan(BaseModel):
    subject: str
    title: str
    task_type: str
    pages_count: int
    difficulty: int
    start_date: date_type
    test_date: date_type
    preferred_start_time: time
    max_minutes_per_day: int = 45

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
class StudyPlanBlock(BaseModel):
    id: int
    title: str
    date: str
    start_time: str
    end_time: str
    minutes: int

class StudyPlanResponse(BaseModel):
    total_minutes: int
    block_count: int
    blocks: list[StudyPlanBlock]
    message: str
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

@router.post("/study_plan", response_model=StudyPlanResponse, status_code=status.HTTP_201_CREATED)
def create_study_plan(current_user: Annotated[User, Depends(get_current_user)],
    data: StudyPlan,
    db: Session = Depends(get_db), predictor: StudyPredict = Depends(get_predictor)):

    if data.max_minutes_per_day<=0:
        raise HTTPException(status_code=400, detail="Max minutes per day must be greater than 0")
    if data.start_date >= data.test_date:
        raise HTTPException(status_code=400, detail="Start date must be before test date")
    days_until_test = (data.test_date - data.start_date).days
    total_minutes = predictor.predict_time(subject=data.subject, task_type=data.task_type,difficulty=data.difficulty, pages_count=data.pages_count, days_until_test=days_until_test)
    result = split_into_study_blocks(total_minutes=total_minutes,start_date=data.start_date,test_date=data.test_date,preferred_start=data.preferred_start_time,max_minutes_per_day=data.max_minutes_per_day)
    scheduled_minutes = sum(block["minutes"] for block in result["blocks"])
    if scheduled_minutes < total_minutes:
        raise HTTPException(status_code=400, detail="Not enough days before test date to schedule all study minutes")

    created_events = []
    for block in result["blocks"]:
        event= Event(
            user_id=current_user.id,
            title=data.title,
            event_date=block["date"],
            start_time=block["start"],
            end_time=block["end"],
            predicted_minutes=block["minutes"],
        )
        db.add(event)
        created_events.append((event, block))
    db.commit()
    response_blocks = []
    for event, block in created_events:
        db.refresh(event)
        response_blocks.append(StudyPlanBlock(
            id=event.id,
            title=event.title,
            date=str(event.event_date),
            start_time=str(event.start_time),
            end_time=str(event.end_time),
            minutes=block["minutes"],
        ))

    return StudyPlanResponse(
        total_minutes=result["total_minutes"],
        block_count=len(response_blocks),
        blocks=response_blocks,
        message="Study plan was created.",
    )

def split_into_study_blocks(total_minutes, start_date, test_date, preferred_start, max_minutes_per_day):
    available_d = (test_date - start_date).days
    block_count = ceil(total_minutes/ max_minutes_per_day)
    block_count = min(available_d, block_count)
    base_minute = total_minutes // block_count
    extra = total_minutes % block_count
    spacing = available_d / block_count
    blocks = []
    for i in range(block_count):
        block_m= base_minute
        if i < extra:
            block_m+= 1
        day_off= int(i * spacing)
        cur_date = start_date+timedelta(days=day_off)
        start_d= datetime.combine(cur_date, preferred_start)
        end_d= start_d + timedelta(minutes=block_m)

        blocks.append({
            "date": cur_date,
            "start": start_d.time(),
            "end": end_d.time(),
            "minutes": block_m,
        })

    return {"total_minutes": total_minutes,"block_count": len(blocks), "blocks": blocks}
