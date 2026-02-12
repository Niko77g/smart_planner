import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from app.predictor import StudyPredict
from app.ml.training_data import training_data

# train the ML model and save in the file
def main():
    predictor = StudyPredict()
    predictor.train_and_save(training_data)
    test_cases = [
        {"subject": "matematika", "task_type": "cvicenia", "difficulty": 4,
         "pages_count": 15, "days_until_test": 7},
        {"subject": "informatika", "task_type": "programovanie", "difficulty": 5,
         "pages_count": 1, "days_until_test": 7},
        {"subject": "dejepis", "task_type": "citanie", "difficulty": 2,
         "pages_count": 30, "days_until_test": 14},
    ]

    for test in test_cases:
        minutes = predictor.predict_time(**test)
        print(f"   {test['subject']}, {test['task_type']} → {minutes} minút")


if __name__ == "__main__":
    main()