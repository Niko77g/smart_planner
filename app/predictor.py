from app.my_calendar import CalendarControl
from datetime import datetime, timedelta, date, time
import joblib
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder


class StudyPredict:
    def __init__(self): #constructor (lazy loading)
        self.model_p =Path("models/model.joblib")
        self.model= None
        self.subject_encode= None
        self.task_type_encode= None
        self._load_model()
        self._calendar = None
    @property  # getter
    def calendar(self):
        if self._calendar is None:
            self._calendar = CalendarControl()
        return self._calendar

    def _load_model(self): # private function
        if self.model_p.exists():
            data = joblib.load(self.model_p)
            self.model = data['model']
            self.subject_encode = data['subject_encode']
            self.task_type_encode = data['task_type_encode']
        else:
            self.model = None
            self.subject_encode = None
            self.task_type_encode = None
            print("Error")

    def train_and_save(self,training_data: list[dict]): # use Facade pattern
        df = pd.DataFrame(training_data)
        self.subject_encode = LabelEncoder()
        self.task_type_encode = LabelEncoder()
        df['task_type'] = self.task_type_encode.fit_transform(df['task_type']) # train and use
        df['subject'] = self.subject_encode.fit_transform(df['subject'])
        #Feature target
        X= df[["subject","task_type","difficulty", "pages_count","days_until_test"]]
        y= df["time_minutes"]
        #train
        self.model = LinearRegression().fit(X,y) # self. -> atribut
        self.model= RandomForestRegressor(n_estimators=100, random_state=42).fit(X,y)

        self.model_p.parent.mkdir(parents=True, exist_ok=True) # created directory if doesnt exist

        joblib.dump({"model": self.model,"subject_encode": self.subject_encode,
        "task_type_encode": self.task_type_encode}, self.model_p) # saving model into directory
    def predict_time(self, subject: str, task_type: str, difficulty: int,pages_count: int, days_until_test: int):
        if self.model is None:
                raise Exception("Model not loaded")
        # returns 0 if subject was not seen during training
        try:
            subject_encode = self.subject_encode.transform([subject])[0] # transform -> convert from string to int, [0] first element and expected list
        except ValueError:
            subject_encode=0

        try:
            task_type_encode = self.task_type_encode.transform(task_type)[0]
        except ValueError:
            task_type_encode=0
        # Feature DataFrame for model prediction
        X= pd.DataFrame([{"subject": subject_encode, "task_type": task_type_encode, "difficulty": difficulty,"pages_count": pages_count,"days_until_test": days_until_test}])

        prediction = self.model.predict(X)[0]
        return max(15, int(round(prediction))) # min. 15 mins for predict

    def create_study_bridge(self, subject: str, task_type: str, difficulty: int, pages_count: int, days_until_test: int, study_date: date,
        start_time: time):
        # get ML prediction for study time
        predicted = self.predict_time(subject=subject, task_type=task_type, difficulty= difficulty, pages_count= pages_count, days_until_test= days_until_test)
        print(predicted)
        #count end time based predicted time
        start_dt = datetime.combine(study_date, start_time)
        end_dt = start_dt + timedelta(minutes=predicted)
        end_time = end_dt.time()
        # formatting event title
        title = f"{subject.title()} - {task_type}"
        # create events by Google Calendar API
        event = self.calendar.add_event(
            title=title,
            start=start_time,
            end=end_time,
            d=study_date
        )
        return { "event_id": event["id"],
            "title": title,
            "date": str(study_date),
            "start": str(start_time),
            "end": str(end_time),
            "predicted_minutes": predicted}

