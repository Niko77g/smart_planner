from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_predict_api():
    response = client.post("/events/predict",
                           json={"subject":"dejepis","difficulty":1,"task_type":"pisanie","pages_count":10,"days_until_test":7})
    assert response.status_code == 200
    data = response.json() # convert JSON to Python dict
    assert "formatted" in data
    assert "predicted_minutes" in data
    assert "days_until_test" in data
    assert data["predicted_minutes"] >=0
    assert data["days_until_test"] >= 0
    assert isinstance(data["daily_minutes"], int)

def test_smart_api():
    response = client.post("/events/smart",json={
        "subject":"dejepis",
        "task_type":"pisanie",
        "difficulty":1,
        "pages_count":10,
        "days_until_test":7,
        "start_time": "16:00:00",
        "end_time": "17:00:00",
        "study_date": "2026-02-10"
    })
    # 401 vyzaduje login
    assert response.status_code == 401

def test_empty_field():
    response =client.post("/events/smart", json={"subject":"dejepis"})
    assert response.status_code == 401

def test_empty_api():
    response = client.post("/events/smart",json={})
    assert response.status_code == 401



