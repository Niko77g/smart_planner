from fastapi import APIRouter
from fastapi.testclient import TestClient
from app.router.events import list_events, create_event

router = APIRouter()

def test_create_event():
    response = router.get("/events")
    assert response.status_code == 200
    assert response.json() == {}
