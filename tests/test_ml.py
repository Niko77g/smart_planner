from fastapi.testclient import TestClient
from app.predictor import StudyPredict
from app.main import app

client = TestClient(app)

def test_load_data():
    study_predict = StudyPredict()
    assert study_predict.model is not None

def test_return_positive():
    study_predict = StudyPredict()
    result =study_predict.predict_time(subject="matematika", task_type="cvicenia", difficulty=2, pages_count=12, days_until_test=9)
    assert result > 0

def test_more_pages():
    study_predict = StudyPredict()

    pages = study_predict.predict_time(subject="slovensky jazyk", task_type="pisanie", difficulty=4, pages_count=2, days_until_test=9)
    more_pages = study_predict.predict_time(subject="slovensky jazyk", task_type="pisanie", difficulty=4, pages_count=40, days_until_test=9)
    assert more_pages > pages