# Phishing Labs

**Fishing Website Classification Using Cloud Classifier Through Web Features on the Cloud**

A four-layer system that takes a URL, extracts 10 numeric features from it, runs those
features through a Random Forest classifier, and returns a prediction (Phishing /
Legitimate), a risk score, a confidence percentage, and a plain-language explanation.

## Architecture

```
Browser (HTML/CSS/JS)
   |
   v
Flask API  (/api/analyze, /api/history)
   |
   v
Feature Extraction  (feature_extraction.py)
   |
   v
Random Forest Model  (model/phishing_model.pkl)
   |
   v
JSON Response  ->  Browser
```

## Project structure

```
Phishing-Labs/
├── backend/
│   ├── app.py                 # Flask API (also serves the frontend)
│   ├── feature_extraction.py  # URL -> 10 numeric features
│   ├── explanation.py         # features -> plain-language reasons
│   ├── db.py                  # SQLite scan history
│   └── requirements.txt
├── frontend/
│   ├── index.html              # Home / URL scanner
│   ├── result.html             # Scan result
│   ├── history.html            # Scan history table
│   ├── about.html              # How it works
│   ├── style.css
│   └── script.js
├── model/
│   ├── train_model.py
│   ├── evaluate_model.py
│   ├── phishing_model.pkl      # trained model (already included)
│   ├── feature_columns.pkl     # feature column order (already included)
│   └── test_data.csv           # held-out test split, for evaluate_model.py
├── data/
│   ├── generate_dataset.py     # builds raw_urls.csv + phishing_dataset.csv
│   ├── raw_urls.csv            # raw URLs + label (already included)
│   └── phishing_dataset.csv    # extracted features + label (already included)
├── database/
│   └── database.db             # created automatically on first run
├── README.md
└── .gitignore
```

## Setup

```bash
cd Phishing-Labs
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
```

A trained model and dataset are already included, so you can skip straight to **Run it**
below. If you want to regenerate everything from scratch:

```bash
cd data
python generate_dataset.py      # rebuilds raw_urls.csv and phishing_dataset.csv
cd ../model
python train_model.py           # retrains and overwrites phishing_model.pkl
python evaluate_model.py        # prints evaluation metrics
```

## Run it

```bash
cd backend
python app.py
```

Open **http://127.0.0.1:5000** in your browser. The Flask server serves both the API and
the frontend from the same origin, so there's no CORS setup needed and no separate
static file server required.

## On the dataset (read this before your viva)

A real live-scraped phishing feed (PhishTank/OpenPhish) needs ongoing internet access
and goes stale immediately, which isn't practical for a college project that needs to
be reproducible offline. Instead, `data/generate_dataset.py` builds a dataset from:

- **~95 real, well-known legitimate domains**, expanded into realistic URL variations
  (subdomains, paths, query strings, and a small % of plain HTTP to avoid the model
  trivially learning "HTTPS = safe").
- **Synthetically generated phishing-style URLs** built from documented real-world
  phishing patterns: raw IP addresses, brand-name typosquats (`paypa1`, `g00gle`),
  `@`-symbol redirection tricks, excessive subdomains, suspicious TLDs (`.tk`, `.ru`,
  `.xyz`...), and keyword stuffing (`secure`, `verify`, `login`...). About 30% of these
  also use HTTPS, since modern phishing kits commonly use free TLS certificates too.

This is a **representative, teaching-purpose dataset**, not a live threat-intelligence
feed — say so plainly if asked. It's good enough to demonstrate the full four-layer
pipeline and produce a genuinely trained, evaluated model, but it does not claim to
generalize to every phishing technique in the wild.

## Evaluation results (actual, from this trained model)

Dataset: 1,300 URLs (650 legitimate / 650 phishing), 80/20 train-test split.

```
Train accuracy: 0.9971
Test accuracy:  0.9923

              precision    recall  f1-score   support
  legitimate       1.00      0.98      0.99       130
    phishing       0.98      1.00      0.99       130
    accuracy                           0.99       260

Confusion matrix (rows=actual, cols=predicted, [legit, phishing]):
[[128   2]
 [  0 130]]
```

**Feature importances** (which features the model actually relies on):

| Feature | Importance |
|---|---|
| num_hyphens | 0.312 |
| num_digits | 0.143 |
| has_https | 0.138 |
| domain_length | 0.104 |
| num_subdomains | 0.103 |
| num_dots | 0.081 |
| url_length | 0.051 |
| num_special_chars | 0.043 |
| has_at_symbol | 0.016 |
| has_ip | 0.008 |

**Honest caveats to include in your report:**
- 99.2% accuracy reflects a synthetic, cleanly-labeled dataset. Real-world phishing
  URLs (especially ones designed to mimic legitimate structure closely) would be
  harder to catch with these 10 lexical features alone — a production system would
  also want page-content and domain-age/WHOIS-based features.
- HTTPS presence is a top-5 feature but is **not** treated as a standalone rule —
  `has_https` gets meaningful weight, not a hard override, which is why the About
  page and result explanations never claim HTTPS alone means "safe."
- The model is not claimed to be 100% accurate anywhere in the code, UI copy, or
  this README, per the project's own requirement.

## API reference

| Endpoint | Method | Body | Returns |
|---|---|---|---|
| `/api/analyze` | POST | `{"url": "..."}` | prediction, risk_score, confidence, features, reasons |
| `/api/history` | GET | - | last 20 scans from SQLite |
| `/api/health` | GET | - | `{"status": "ok"}` |

## Cloud deployment notes

For deploying this beyond localhost (e.g. a free tier on Render/Railway/PythonAnywhere):
- Set `debug=False` in `app.py` for any non-local deployment.
- Run behind a production WSGI server (`gunicorn app:app`) instead of Flask's dev server.
- SQLite works for a single-instance demo deployment; it is not suitable for multiple
  concurrent server instances — a college-project cloud deployment on one instance is fine.
- The `model/*.pkl` files must be included in the deployment — they are not regenerated
  automatically at startup.
