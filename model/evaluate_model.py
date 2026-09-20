import os
import pandas as pd
import joblib
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)

BASE_DIR = os.path.dirname(__file__)

model = joblib.load(os.path.join(BASE_DIR, 'phishing_model.pkl'))
feature_columns = joblib.load(os.path.join(BASE_DIR, 'feature_columns.pkl'))

test_df = pd.read_csv(os.path.join(BASE_DIR, 'test_data.csv'))
X_test = test_df[feature_columns]
y_test = test_df['label']

y_pred = model.predict(X_test)

print("=== Evaluation on held-out test set ===")
print(f"Accuracy:  {accuracy_score(y_test, y_pred):.4f}")
print(f"Precision: {precision_score(y_test, y_pred):.4f}")
print(f"Recall:    {recall_score(y_test, y_pred):.4f}")
print(f"F1 score:  {f1_score(y_test, y_pred):.4f}")

print("\nConfusion matrix (rows=actual, cols=predicted, order=[legit, phishing]):")
print(confusion_matrix(y_test, y_pred))

print("\nClassification report:")
print(classification_report(y_test, y_pred, target_names=['legitimate', 'phishing']))

print("\nFeature importances:")
importances = pd.Series(model.feature_importances_, index=feature_columns)
print(importances.sort_values(ascending=False))
