import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, '..', 'data', 'phishing_dataset.csv')

df = pd.read_csv(DATA_PATH)

X = df.drop(columns=['label'])
y = df['label']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

train_acc = accuracy_score(y_train, model.predict(X_train))
test_acc = accuracy_score(y_test, model.predict(X_test))
print(f"Train accuracy: {train_acc:.4f}")
print(f"Test accuracy:  {test_acc:.4f}")

joblib.dump(model, os.path.join(BASE_DIR, 'phishing_model.pkl'))
joblib.dump(list(X.columns), os.path.join(BASE_DIR, 'feature_columns.pkl'))

test_df = X_test.copy()
test_df['label'] = y_test
test_df.to_csv(os.path.join(BASE_DIR, 'test_data.csv'), index=False)

print("Saved phishing_model.pkl, feature_columns.pkl, and test_data.csv")
