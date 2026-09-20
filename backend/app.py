import os
import sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import joblib

sys.path.append(os.path.dirname(__file__))
from feature_extraction import extract_features
from explanation import generate_explanation
from db import init_db, save_scan, get_recent_scans

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'frontend')

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)

MODEL_PATH = os.path.join(BASE_DIR, '..', 'model', 'phishing_model.pkl')
COLUMNS_PATH = os.path.join(BASE_DIR, '..', 'model', 'feature_columns.pkl')

model = joblib.load(MODEL_PATH)
feature_columns = joblib.load(COLUMNS_PATH)

init_db()


# ---------- Serve the frontend (so the whole app runs from one server) ----------
@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(FRONTEND_DIR, filename)


# ---------- API ----------
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})


@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.get_json(silent=True)
    if not data or not data.get('url'):
        return jsonify({"error": "Missing 'url' in request body"}), 400

    url = data['url'].strip()
    if not url:
        return jsonify({"error": "URL cannot be empty"}), 400

    features = extract_features(url)

    # build the feature vector in the exact column order used during training
    X = [[features[col] for col in feature_columns]]

    prediction = model.predict(X)[0]
    probabilities = model.predict_proba(X)[0]  # index 0 = legit, index 1 = phishing

    phishing_prob = float(probabilities[1])
    confidence = float(round(max(probabilities) * 100, 2))
    risk_score = int(round(phishing_prob * 100))

    result = {
        "url": url,
        "prediction": "PHISHING" if prediction == 1 else "LEGITIMATE",
        "risk_score": risk_score,
        "confidence": confidence,
        "features": features,
        "reasons": generate_explanation(features)
    }

    save_scan(url, result['prediction'], result['risk_score'], result['confidence'])

    return jsonify(result)


@app.route('/api/history', methods=['GET'])
def history():
    scans = get_recent_scans(limit=20)
    return jsonify(scans)


if __name__ == '__main__':
    app.run(debug=False, port=5000)
