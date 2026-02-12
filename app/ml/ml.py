
from abc import ABC, abstractmethod
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
import pandas as pd
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import training_data as data

df = pd.DataFrame(data.training_data)
print(df.head())
en_subject = LabelEncoder()
df["subject_encode"] = en_subject.fit_transform(df["subject"])
en_task_type = LabelEncoder()
df["task_type_encode"] = en_task_type.fit_transform(df["task_type"])


feature_columns = [
    "subject_encode",
    "task_type_encode",
    "difficulty",
    "pages_count",
    "days_until_test"
]
X = df[feature_columns]
y = df["time_minutes"]
 #split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

#print("\n Data split:")
#print(f"Training samples: {len(X_train)} ({len(X_train)/len(X)*100:.0f}%)")
#print(f"Test samples:     {len(X_test)} ({len(X_test)/len(X)*100:.0f}%)")

class StrategyML(ABC):
    @abstractmethod
    def train(self,X,y):
        pass
    @abstractmethod
    def predict(self,X):
        pass

class LinearStrategy(StrategyML):
    def __init__(self):
        self.model = LinearRegression()
    def train(self,X,y):
        self.model.fit(X,y)
    def predict(self,X):
        return self.model.predict(X)
    def get_name(self):
        return "Linear Regression"

class RandomForestStrategy(StrategyML):
    def __init__(self):
        self.model = RandomForestRegressor()
    def train(self,X,y):
        self.model.fit(X,y)
    def predict(self,X):
        return self.model.predict(X)
    def get_name(self):
        return "Random Forest"



strategies= [LinearStrategy(),RandomForestStrategy()]
results={}
for strategy in strategies:
    strategy.train(X_train,y_train)
    y_pred = strategy.predict(X_test)
    # metrics
    mea_lr = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    results[strategy.get_name()] = {"mae": mea_lr, "r2": r2}
    print(strategy.get_name())
    print(f"MEA {mea_lr}")
    print(f"R2 {r2}")







